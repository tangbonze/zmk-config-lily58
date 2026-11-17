# 下载依赖到 ./dependencies
init-standalone:
	west init -l config --mf west-isolated.yml
	west update --narrow
	west zephyr-export

# 下载依赖到 ../（workspace 模式）
init-workspace:
	west init -l . --mf config/west.yml
	west update --narrow
	west zephyr-export

# 按 build.yaml 全量编译
build-all:
	west zmk-build -d ./build -q

# 临时编一个带 USB 日志的诊断固件
debug-all:
	west zmk-build -S zmk-usb-logging
