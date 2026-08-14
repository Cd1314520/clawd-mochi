# Clawd Mochi — Chris 定制版 v0.2.0

> **版本代号：Connected Desk Pet**

这份固件基于上游项目 `yousifamanuel/clawd-mochi` 的 `main` 分支提交
`0a8e9f6`（2026-06-28）。本地定制固件位于
[`clawd_mochi/clawd_mochi.ino`](clawd_mochi/clawd_mochi.ino)。

## 已加入的功能

- STA Wi-Fi 模式：Mochi 可加入本地网络，不必让手机切换到它自己的热点。
- 固定 IP、自动重连与断网恢复。
- `/notify` HTTP 接口：脚本或 Claude Code 可让 Mochi 换脸、显示消息、闪绿/红警报或呼吸提醒。
- 浏览器 HTTP 无线更新：使用 `/update` 推送新的固件，不依赖 Arduino IDE 的网络端口。
- 电脑锁屏时睡觉、解锁时醒来；睡眠断网过久会自动醒来，避免卡在黑屏状态。
- 自动眨眼、瞟眼、夜间调暗背光。
- 十张随机轮换的表情脸。
- Claude Code 状态联动：完成时开心、失败时红色警报、等待输入时呼吸提醒。

## 发布到 GitHub 前必须做的事

**不要直接发布当前固件。** `clawd_mochi.ino` 中的 `STA_SSID` 与
`STA_PASS` 目前是本机网络凭据，发布前必须替换为：

```cpp
const char* STA_SSID = "";
const char* STA_PASS = "";
```

用户可自行填写 Wi-Fi 名称和密码；留空时，Mochi 保持原版热点模式。

## 推荐发布方式

先作为个人 Fork 发布，版本名使用 **v0.2.0 — Connected Desk Pet**。
其中通用的部分（STA 模式、通知接口、HTTP 更新等）可以后续整理成独立 PR 回馈给上游项目。
