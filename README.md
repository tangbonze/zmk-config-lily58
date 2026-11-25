# zmk-config-lily58

[English](./README.en.md) · **简体中文**

Lily58 分体键盘的 ZMK 固件配置，已接入 [DYA Studio](https://studio.dya.cormoran.works/)，
一次编译同时输出 **板载 OLED** 与 **nice!view** 两套固件。

## 关于 Lily58

[Lily58](https://github.com/kata0510/Lily58) 是 kata0510 设计的开源 58 键分体人体工学键盘
（单侧 6×4 + 数字行 + 5 枚底部/拇指键），键数适中、保留完整数字行，
非常适合从传统键盘过渡到分体列错位布局。

| 项目 | 说明 |
| --- | --- |
| 微控制器 | nice!nano v2（`nice_nano//zmk`）/ 其他 Pro Micro 引脚兼容板 |
| 轴座 | Classic Pro 支持 MX 与 Choc 轴体（本配置采用标准 Lily58 矩阵） |
| 显示 | 板载 0.91" SSD1306 OLED（128×32）或 nice!view 扩展屏 |
| 分体通信 | BLE 无线分体（`CONFIG_ZMK_KEYBOARD_NAME="Lily58 DYA"`） |
| 物理布局 | 来自 `cormoran/zmk` 内置 `app/dts/layouts/kata0510/lily58.dtsi` |

> 本仓库的 `3dmodel/` 与 `refers/` 目录保留了外壳 3D 模型（`.3mf`）与硬件参考图，方便改造与装机对照。

## 固件变体

GitHub Actions → 最新一次构建 → Artifacts → `lily58-firmware`，一次编译输出以下 5 个 `.uf2`：

| Artifact | 适用半边 | 说明 |
| --- | --- | --- |
| `lily58_left_oled` | 左手（central） | 板载 SSD1306 OLED + DYA Studio + ZMK KeyTester |
| `lily58_right_oled` | 右手（peripheral） | 板载 SSD1306 OLED |
| `lily58_left_niceview` | 左手（central） | nice!view 适配板 + DYA Studio + ZMK KeyTester |
| `lily58_right_niceview` | 右手（peripheral） | nice!view 适配板 |
| `settings_reset` | 任一半边 | 清除所有持久化设置（含 DYA Studio 保存的配置） |

- **OLED 变体**：启用 `lily58-oled` snippet（`CONFIG_ZMK_DISPLAY=y` 及电量百分比显示）。
- **nice!view 变体**：在 shield 中追加 `nice_view_adapter nice_view`，并通过 `lily58-no-display` snippet 显式设置 `CONFIG_SSD1306=n`，避免两套显示驱动同时编译进固件。
- **`settings_reset`**：刷完重置固件后再刷回正常固件即可。

## DYA Studio

浏览器打开 <https://studio.dya.cormoran.works/>，按页面提示选择连接方式：

| 方式 | 说明 | 支持的浏览器 |
| --- | --- | --- |
| USB | 插线后选择串口（Web Serial） | Chrome / Edge（桌面） |
| Bluetooth | 配对后通过 BLE 连接（Web Bluetooth） | Chrome / Edge（桌面）、Android Chrome、iOS Bluefy |
| Demo | 无需键盘，模拟界面试用全部功能 | 同上 |

Firefox 与 Safari 不支持 Web Serial / Web Bluetooth。

### 可用功能

- **Keymap Editor** — 可视化编辑键位与图层，支持按键实时高亮
- **Macros & Combos** — 网页端直接创建运行时宏与组合键，**无需重新编译固件**
- **Connection Management** — BLE 配置档重命名 / 切换 / 解绑
- **Device Settings** — 电源管理（idle / deep sleep 超时等），并经分体事件中继同步到右手
- **Troubleshooting** — 电量历史、固件版本、uptime、看门狗与逐键抖键诊断
- **OS Detection & Default Layer** — 根据 USB / BLE 连接主机系统自动切换默认层

### 左右半分配

**本键盘的 central（主控）是左手** —— USB 与 BLE 都连接左手，DYA Studio 也只会连上左手。

| | 左手 · central | 右手 · peripheral |
| --- | --- | --- |
| **刷哪个固件** | **`lily58_left_*`** | **`lily58_right_*`** |
| USB / BLE 连接 | 是 | — |
| Studio RPC 通信 | 是 | — |
| 连接管理、OS 识别、默认层 | 是 | — |
| 设置中继 | 发起 | 接收并应用 |
| 抖键诊断、看门狗 | 汇总两半 | 检测本半并上报 |
| ZMK KeyTester（Raw HID） | 是 | — |

> ⚠️ **刷反半边会导致键盘完全无输入**（两半无法配对通信）。请务必确认左手刷 `lily58_left_*`、右手刷 `lily58_right_*`。

### Studio 锁定状态

`snippets/lily58-central/lily58-central.conf` 默认设置了 `CONFIG_ZMK_STUDIO_LOCKING=n`：
固件上电与断开重连后**保持常开（unlocked）**状态，无需先按解锁键即可直接连接 DYA Studio。

### 默认键位

`config/lily58.keymap` 移植自 `kata0510/qmk_firmware`（`add_lily58_rev2` 分支 `keyboards/lily58_rp2040/keymaps/default/keymap.c`），包含 4 层基础布局：

- **Layer 0 (`default_layer`)**：标准 QWERTY + 数字行，拇指区提供 `&mo 1` / `&lt 1 SPACE`（LOWER）与 `&lt 2 ENTER` / `&mo 2`（RAISE）
- **Layer 1 (`lower_layer`)**：数字符号与小键盘区排布
- **Layer 2 (`raise_layer`)**：`F1`–`F12`、方向键及常用符号
- **Layer 3 (`adjust_layer`)**：空白保留层（可在 DYA Studio 中按需自定义）

## ZMK KeyTester（物理矩阵测试）

本仓库已在 central 半边集成 [tangbonze/zmk-matrix-tester](https://github.com/tangbonze/zmk-matrix-tester)
模块（开启 `CONFIG_ZMK_MATRIX_TESTER=y` 与 `CONFIG_USB_HID_DEVICE_COUNT=2`），配合
[ZMK KeyTester](https://github.com/tangbonze/zmk-keyboard-tester) 网页端可进行物理矩阵直读测试：

1. 将左手（central）通过 USB 数据线连接到电脑（桌面版 Chrome / Edge）。
2. 打开预载本仓库配置的在线测试页：
   <https://tangbonze.github.io/zmk-keyboard-tester/?config=https://github.com/tangbonze/zmk-config-lily58>
3. 点击顶部 **「WebHID 物理矩阵」**，选择 `Lily58 DYA` 即可实时点亮左右手物理按键，验证轴体与焊接。

## 本地构建

需要 **Python 3.12**、`west` 与 [Zephyr SDK 0.17.0](https://docs.zephyrproject.org/latest/develop/toolchains/index.html)：

```bash
export ZEPHYR_SDK_INSTALL_DIR=~/zephyr-sdk-0.17.0

# 1. 初始化并拉取依赖到 ./dependencies（或用 make init-workspace 拉取到上一级目录）
make init-standalone

# 确保 Studio protobuf 代码生成所需依赖已安装
pip install "protobuf>=5.27" grpcio-tools

# 2. 按 build.yaml 全量编译（OLED + nice!view + settings_reset）
make build-all

# 或单独编译某一个目标 / 刷写
west zmk-build -a lily58_left_oled -p always
west zmk-build -a lily58_left_niceview --flash

# 临时编译带 USB 日志的诊断固件
make debug-all
```

构建产物位于 `./build/<artifact>/zephyr/zmk.uf2`。

## 目录结构

```
.github/workflows/build.yml   CI 自动编译并打包 lily58-firmware
3dmodel/                      外壳与配件 3D 模型（.3mf）
refers/                       硬件焊接与装机参考图
config/
  lily58.conf                 两半共用的通用 Kconfig（蓝牙、电池、电源管理、栈大小等）
  lily58.keymap               4 层基础键位定义（QWERTY / LOWER / RAISE / ADJUST）
  west-dependency.yml         依赖清单：cormoran/zmk main+dya + DYA 模块栈 + zmk-matrix-tester
  west-isolated.yml           将依赖下载到 ./dependencies
  west.yml                    默认 west manifest 入口
snippets/
  lily58-central/             左手专用 Kconfig（ZMK Studio、*_STUDIO_RPC、KeyTester 等）
  lily58-peripheral/          右手专用 Kconfig（仅接收并应用中继设置）
  lily58-oled/                板载 OLED 显示开关
  lily58-no-display/          关闭板载 SSD1306，供 nice!view 变体使用
zephyr/module.yml             声明 snippet_root 与 board_root
build.yaml                    固件构建矩阵（同时包含 OLED、nice!view 与 settings_reset）
Makefile                      本地初始化与编译快捷命令
```

### 为什么用 snippet 按半边拆分配置

DYA Studio 的 `*_STUDIO_RPC` 依赖 protobuf 桩代码，该桩代码只在 central 半边生成；
如果写入全局 `lily58.conf`，右手（peripheral）编译时会因缺少 `proto/zmk/custom.pb.h` 而失败。
同时 Zephyr 会优先加载 ZMK 上游 `app/boards/shields/lily58/`，直接在仓库放 `<shield>.conf` 容易被忽略。
因此本仓库在 `build.yaml` 中通过显式的 `snippets:` 分别注入 `lily58-central` 与 `lily58-peripheral`，保证两半配置严格隔离。

## 依赖来源

- [cormoran/zmk](https://github.com/cormoran/zmk)（`main+dya` 分支）：提供 DYA Studio 所需自定义 Studio RPC 与分体事件中继
- [cormoran/zephyr](https://github.com/cormoran/zephyr)（`v4.1.0+zmk-fixes+nrf-half-duplex-uart`）及 DYA Studio 扩展模块栈
- [tangbonze/zmk-matrix-tester](https://github.com/tangbonze/zmk-matrix-tester)：WebHID 物理矩阵直读测试模块

## License

MIT
