# zmk-config-lily58

**English** · [简体中文](./README.md)

ZMK firmware configuration for the Lily58 split keyboard with
[DYA Studio](https://studio.dya.cormoran.works/) support. A single build outputs
firmware for both **onboard OLED** and **nice!view** variants.

## About Lily58

[Lily58](https://github.com/kata0510/Lily58) is an open-source 58-key split
ergonomic keyboard designed by kata0510 (6×4 columns + number row + 5 thumb/bottom
keys per half), offering a full number row for an easier transition from standard keyboards.

| Item | Detail |
| --- | --- |
| Microcontroller | nice!nano v2 (`nice_nano//zmk`) / other Pro Micro footprint boards |
| Switches | Classic Pro supports MX and Choc (uses standard Lily58 matrix) |
| Display | Onboard 0.91" SSD1306 OLED (128×32) or nice!view adapter |
| Split Link | Wireless BLE split (`CONFIG_ZMK_KEYBOARD_NAME="Lily58 DYA"`) |
| Physical Layout | Built-in `app/dts/layouts/kata0510/lily58.dtsi` from `cormoran/zmk` |

> The `3dmodel/` and `refers/` directories retain case 3D models (`.3mf`) and hardware reference images.

## Firmware Variants

GitHub Actions → latest run → Artifacts → `lily58-firmware` contains all 5 `.uf2` images from one build:

| Artifact | Half | Description |
| --- | --- | --- |
| `lily58_left_oled` | Left (central) | Onboard SSD1306 OLED + DYA Studio + ZMK KeyTester |
| `lily58_right_oled` | Right (peripheral) | Onboard SSD1306 OLED |
| `lily58_left_niceview` | Left (central) | nice!view adapter + DYA Studio + ZMK KeyTester |
| `lily58_right_niceview` | Right (peripheral) | nice!view adapter |
| `settings_reset` | Either half | Clears persisted Zephyr / DYA Studio settings |

- **OLED variant**: enables `lily58-oled` snippet (`CONFIG_ZMK_DISPLAY=y` with battery percentage widget).
- **nice!view variant**: appends `nice_view_adapter nice_view` to the shield and applies `lily58-no-display` (`CONFIG_SSD1306=n`) so the onboard SSD1306 driver is disabled.
- **`settings_reset`**: flash once to clear stored settings, then re-flash your normal firmware.

## DYA Studio

Open <https://studio.dya.cormoran.works/> and choose a connection method:

| Method | How | Supported browsers |
| --- | --- | --- |
| USB | Plug in and pick the serial port (Web Serial) | Chrome / Edge (desktop) |
| Bluetooth | Pair and connect over BLE (Web Bluetooth) | Chrome / Edge (desktop), Android Chrome, Bluefy on iOS |
| Demo | Try the full UI with a simulated keyboard | Same as above |

Firefox and Safari are not supported.

### Available Features

- **Keymap Editor** — visual keymap and layer editing with live key press highlighting
- **Macros & Combos** — runtime macros and combos directly in the browser without rebuilding firmware
- **Connection Management** — rename, switch, and unpair BLE profiles
- **Device Settings** — power management (idle / deep sleep timeouts) relayed to the peripheral half
- **Troubleshooting** — battery history, firmware version, uptime, watchdog, and per-key chatter diagnostics
- **OS Detection & Default Layer** — automatic default layer switching based on host OS over USB / BLE

### Which Half Is Which

**The left half is central** — connect USB and BLE to the left half; DYA Studio only connects to the central half.

| | Left · central | Right · peripheral |
| --- | --- | --- |
| **Firmware to flash** | **`lily58_left_*`** | **`lily58_right_*`** |
| USB / BLE host link | Yes | — |
| Studio RPC | Yes | — |
| Connection management, OS detection, default layer | Yes | — |
| Settings relay | Originates | Receives & applies |
| Chatter diagnostics, watchdog | Aggregates both halves | Reports own half |
| ZMK KeyTester (Raw HID) | Yes | — |

> ⚠️ **Flashing the wrong half leaves the keyboard unresponsive** because central and peripheral will not pair. Always flash `lily58_left_*` on the left half and `lily58_right_*` on the right half.

### Studio Locking

`snippets/lily58-central/lily58-central.conf` sets `CONFIG_ZMK_STUDIO_LOCKING=n`,
keeping ZMK Studio **unlocked by default** across power cycles and reconnects.

### Default Keymap

`config/lily58.keymap` is ported from `kata0510/qmk_firmware` (`add_lily58_rev2`,
`keyboards/lily58_rp2040/keymaps/default/keymap.c`) with 4 layers:

- **Layer 0 (`default_layer`)**: standard QWERTY + number row, thumb keys `&mo 1` / `&lt 1 SPACE` (LOWER) and `&lt 2 ENTER` / `&mo 2` (RAISE)
- **Layer 1 (`lower_layer`)**: symbols and number row layout
- **Layer 2 (`raise_layer`)**: `F1`–`F12`, arrow keys, and common symbols
- **Layer 3 (`adjust_layer`)**: blank layer reserved for customization in DYA Studio

## ZMK KeyTester (Physical Matrix Test)

The central half integrates [tangbonze/zmk-matrix-tester](https://github.com/tangbonze/zmk-matrix-tester)
(`CONFIG_ZMK_MATRIX_TESTER=y`, `CONFIG_USB_HID_DEVICE_COUNT=2`) for hardware-level
matrix testing in [ZMK KeyTester](https://github.com/tangbonze/zmk-keyboard-tester):

1. Connect the left half (central) via USB on desktop Chrome or Edge.
2. Open the pre-configured tester URL:
   <https://tangbonze.github.io/zmk-keyboard-tester/?config=https://github.com/tangbonze/zmk-config-lily58>
3. Click **WebHID Physical Matrix** and select `Lily58 DYA` to test every switch across both halves.

## Local Build

Requires **Python 3.12**, `west`, and [Zephyr SDK 0.17.0](https://docs.zephyrproject.org/latest/develop/toolchains/index.html):

```bash
export ZEPHYR_SDK_INSTALL_DIR=~/zephyr-sdk-0.17.0

# 1. Initialize workspace and fetch dependencies into ./dependencies
make init-standalone

# Install protobuf dependencies required for Studio codegen
pip install "protobuf>=5.27" grpcio-tools

# 2. Build all targets in build.yaml (OLED + nice!view + settings_reset)
make build-all

# Or build / flash a single target
west zmk-build -a lily58_left_oled -p always
west zmk-build -a lily58_left_niceview --flash

# Build with USB logging enabled for diagnostics
make debug-all
```

Built `.uf2` images are written to `./build/<artifact>/zephyr/zmk.uf2`.

## Directory Structure

```
.github/workflows/build.yml   CI workflow packaging lily58-firmware
3dmodel/                      Case and extension 3D models (.3mf)
refers/                       Hardware wiring and build reference images
config/
  lily58.conf                 Shared Kconfig for both halves (BLE, battery, power, stacks)
  lily58.keymap               4-layer default keymap (QWERTY / LOWER / RAISE / ADJUST)
  west-dependency.yml         Manifest: cormoran/zmk main+dya + DYA stack + zmk-matrix-tester
  west-isolated.yml           Places dependencies under ./dependencies
  west.yml                    Default west manifest entry
snippets/
  lily58-central/             Left-half Kconfig (ZMK Studio, *_STUDIO_RPC, KeyTester, etc.)
  lily58-peripheral/          Right-half Kconfig (settings relay receiver only)
  lily58-oled/                Onboard OLED display configuration
  lily58-no-display/          Disables onboard SSD1306 for nice!view builds
zephyr/module.yml             Declares snippet_root and board_root
build.yaml                    Build matrix (OLED, nice!view, and settings_reset)
Makefile                      Convenience targets for init and local builds
```

### Why Configuration Is Split with Snippets

DYA Studio `*_STUDIO_RPC` options depend on generated protobuf stubs that are only
produced on the central half; putting them in `config/lily58.conf` breaks the peripheral
build due to missing `proto/zmk/custom.pb.h`. Using explicit `snippets:` entries in
`build.yaml` keeps central and peripheral configurations cleanly isolated.

## Dependencies

- [cormoran/zmk](https://github.com/cormoran/zmk) (`main+dya` branch): custom Studio RPC protocol and split event relay
- [cormoran/zephyr](https://github.com/cormoran/zephyr) (`v4.1.0+zmk-fixes+nrf-half-duplex-uart`) and DYA Studio feature modules
- [tangbonze/zmk-matrix-tester](https://github.com/tangbonze/zmk-matrix-tester): WebHID physical matrix testing module

## License

MIT
