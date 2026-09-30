import pyomo.environ as pyo
import numpy as np

def solve_dispatch(horizon_hours, load_forecast, solar_forecast, wind_forecast, temp_forecast,
                   initial_soc, battery_cap=500, gen_cap=150, min_gen_load=0.3,
                   deferrable_loads=[], reserve_margin=0.1):
    """
    Solves 48h dispatch using Pyomo + HiGHS.
    deferrable_loads is a list of dicts: {'id': str, 'total_energy': kw*hours} (for simplicity, we assume they must be consumed over the horizon)
    We will just take a total deferrable energy that needs to be allocated.
    """
    m = pyo.ConcreteModel()
    
    # Sets
    m.T = pyo.RangeSet(0, horizon_hours - 1)
    
    # Parameters
    m.load_demand = pyo.Param(m.T, initialize=lambda m, t: load_forecast[t])
    m.solar = pyo.Param(m.T, initialize=lambda m, t: solar_forecast[t])
    m.wind = pyo.Param(m.T, initialize=lambda m, t: wind_forecast[t])
    
    # Battery derating per timestep
    def batt_cap_rule(m, t):
        tc = temp_forecast[t]
        return max(0.4 * battery_cap, battery_cap * (1.0 - (0 - tc) * 0.015)) if tc < 0 else battery_cap
    m.batt_cap = pyo.Param(m.T, initialize=batt_cap_rule)
    
    def batt_pwr_rule(m, t):
        tc = temp_forecast[t]
        return max(0.2 * 250, 250 * (1.0 - (0 - tc) * 0.02)) if tc < 0 else 250
    m.batt_pwr = pyo.Param(m.T, initialize=batt_pwr_rule)
    
    # Variables
    m.gen_pwr = pyo.Var(m.T, bounds=(0, gen_cap))
    m.gen_on = pyo.Var(m.T, within=pyo.Binary)
    
    m.batt_charge = pyo.Var(m.T, bounds=(0, 250))
    m.batt_discharge = pyo.Var(m.T, bounds=(0, 250))
    m.soc = pyo.Var(m.T, bounds=(0, battery_cap))
    
    # If we have deferrable loads, we can allocate them to each hour
    m.def_load = pyo.Var(m.T, bounds=(0, sum(dl['kw'] for dl in deferrable_loads) if deferrable_loads else 0))
    
    # Slack variable to prevent infeasibility when demand exceeds capacity
    m.shed_load = pyo.Var(m.T, bounds=(0, None))
    
    # Constraints
    def gen_min_rule(m, t):
        return m.gen_pwr[t] >= gen_cap * min_gen_load * m.gen_on[t]
    m.gen_min_c = pyo.Constraint(m.T, rule=gen_min_rule)
    
    def gen_max_rule(m, t):
        return m.gen_pwr[t] <= gen_cap * m.gen_on[t]
    m.gen_max_c = pyo.Constraint(m.T, rule=gen_max_rule)
    
    def batt_charge_limit_rule(m, t):
        return m.batt_charge[t] <= m.batt_pwr[t]
    m.batt_chg_c = pyo.Constraint(m.T, rule=batt_charge_limit_rule)
    
    def batt_discharge_limit_rule(m, t):
        return m.batt_discharge[t] <= m.batt_pwr[t]
    m.batt_dis_c = pyo.Constraint(m.T, rule=batt_discharge_limit_rule)
    
    def soc_limit_rule(m, t):
        return m.soc[t] <= m.batt_cap[t]
    m.soc_lim_c = pyo.Constraint(m.T, rule=soc_limit_rule)
    
    def soc_update_rule(m, t):
        if t == 0:
            return m.soc[t] == initial_soc + m.batt_charge[t] - m.batt_discharge[t]
        return m.soc[t] == m.soc[t-1] + m.batt_charge[t] - m.batt_discharge[t]
    m.soc_upd_c = pyo.Constraint(m.T, rule=soc_update_rule)
    
    def supply_demand_rule(m, t):
        # critical load + deferrable load scheduled at t
        demand = m.load_demand[t] + m.def_load[t]
        supply = m.solar[t] + m.wind[t] + m.gen_pwr[t] + m.batt_discharge[t] + m.shed_load[t]
        return supply == demand + m.batt_charge[t]
    m.sd_c = pyo.Constraint(m.T, rule=supply_demand_rule)
    
    # Deferrable load constraint (must serve all required energy over horizon)
    if deferrable_loads:
        total_def_energy_required = sum(dl['kw'] * horizon_hours for dl in deferrable_loads) # Assuming the API contract means kw is continuous load. Or it means kw is peak, maybe we assume it needs to run for X hours? Let's assume it needs to run for half the horizon
        total_required = sum(dl['kw'] * (horizon_hours // 2) for dl in deferrable_loads)
        def def_energy_rule(m):
            return sum(m.def_load[t] for t in m.T) == total_required
        m.def_energy_c = pyo.Constraint(rule=def_energy_rule)
    
    # Reserve margin constraint
    def reserve_rule(m, t):
        # capacity of gen + max discharge >= demand * (1 + margin)
        # to handle sudden drop in renewable.
        demand = m.load_demand[t] + m.def_load[t]
        available_cap = m.gen_on[t] * gen_cap + m.batt_pwr[t] 
        return available_cap >= demand * reserve_margin
    m.res_c = pyo.Constraint(m.T, rule=reserve_rule)
    
    # Objective: minimize fuel + massive penalty for shedding
    # fuel = base_fuel * gen_on + var_fuel * gen_pwr
    # base = 0.1 * gen_cap, var = 0.25 (as in equipment.py)
    def obj_rule(m):
        return sum(0.1 * gen_cap * m.gen_on[t] + 0.25 * m.gen_pwr[t] + 1000 * m.shed_load[t] for t in m.T)
    m.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)
    
    solver = pyo.SolverFactory('appsi_highs')
    res = solver.solve(m, tee=False)
    
    if (res.solver.status == pyo.SolverStatus.ok) and (res.solver.termination_condition == pyo.TerminationCondition.optimal):
        schedule = []
        for t in m.T:
            schedule.append({
                'time_idx': t,
                'generator_kw': m.gen_pwr[t].value,
                'battery_kw': m.batt_charge[t].value - m.batt_discharge[t].value,
                'deferred_load_kw': m.def_load[t].value,
                'soc_pct': (m.soc[t].value / battery_cap) * 100,
                'soc_kwh': m.soc[t].value
            })
        return schedule, pyo.value(m.obj)
    else:
        return None, None
