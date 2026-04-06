# Renpho for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for Renpho smart scales. Pulls your latest body measurements from the Renpho cloud and exposes them as sensors.

## Sensors

| Sensor | Unit | Notes |
|--------|------|-------|
| Weight | kg | |
| BMI | — | |
| Body Fat | % | Requires bio-impedance scale |
| Body Water | % | Requires bio-impedance scale |
| Muscle Mass | % | Requires bio-impedance scale |
| Bone Mass | kg | Requires bio-impedance scale |
| BMR | kcal | Basal Metabolic Rate |
| Body Age | years | Requires bio-impedance scale |
| Protein | % | Requires bio-impedance scale |
| Visceral Fat | — | Requires bio-impedance scale |

Sensors that the scale did not measure (returned as 0) will show as **Unavailable** rather than 0.

## Requirements

- Renpho account (email + password)
- HACS installed in Home Assistant

## Installation via HACS

1. In HACS, go to **Integrations → Custom repositories**
2. Add this repository URL with category **Integration**
3. Search for **Renpho** and install
4. Restart Home Assistant

## Manual Installation

Copy `custom_components/renpho/` into your `<config>/custom_components/` directory and restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Renpho**
3. Enter your Renpho email and password

Data is refreshed every **60 minutes**. Polling more frequently is not recommended as logging in terminates active sessions in the Renpho mobile app.

## Notes

- This integration uses the [`renpho-api`](https://pypi.org/project/renpho-api/) PyPI package.
- Measurements shown are the most recent weigh-in recorded in the Renpho cloud.

## License

MIT
