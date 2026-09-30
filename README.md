# ensemble_LSM_simulation (update date: July 18th, 2025, Jun 16 2026)

This repository serves as a backup for the three-model simulations over the Scotty Creek site (Northwest Territories, Canada).
```text
boreal-model-intercomparison/
│
├── src/
│   ├── research_domain_plotting/
│   ├── soil moisture/ET/
│   ├── soil temperature/
│   ├── SM-ET relationship/
│   └── cumulative p minus ET/
│
├── data/
│   ├── site raw forcing provided by Prof.Oliver/
│   ├── Noah-MP forcing/
│   ├── CLM forcing/
│   ├── CLASS forcing/
│   ├── research domain shapefile/ 
│   └── validation data (ET,SM,ST)/
│
├── experiments/
│   ├── noahmp/
│   ├── CLM5/
│   └── class/
│
├── figures/
│   ├── figure 1-5
│    
│
└── project output/
    |── manuscript submitted to Journal of hydrology/
    └── oral presentation: Noah-MP 2025 workshop/2026 CGU meeting/
1. how to run CLM model on site level

    1.1 set up CLM model in derecho

    1.2 preparing the forcing data

    1.3 preparing the initial field

3. how to run CLASS model on site level
4. how to run Noah-MP model on site level
