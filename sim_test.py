# from simulations.air_pollutant.air_pollutant import run_sim
from simulations.sky.sky import run_sky

arr = [
    [
        103.8406,
          1.2770
    ],
    [
        103.8407,
          1.2770
    ],
    [
        103.8407,
          1.2771
    ],
    [
        103.8406,
          1.2771
    ]
]

# run_sim(arr)
r = run_sky(arr)
print(r)
