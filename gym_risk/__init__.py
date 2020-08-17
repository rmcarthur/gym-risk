from gym.envs.registration import register

register(
    id='risk-v0',
    entry_point='gym_risk.envs:RiskEnv',
)