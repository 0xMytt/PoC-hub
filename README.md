# PoC-hub

PoC 命名规则（格式）：

```text
{Vendor}{Product}{Version{VulnType}{CVE/CNVD/CustomID}.py
```

字段说明：

| 字段                | 说明                                                         | 占位符          | 示例                     |
| :------------------ | :----------------------------------------------------------- | :-------------- | :----------------------- |
| {Vendor}            | 厂商/开发商名称。小写，无空格                                | unkVendor       | znyx                     |
| {_PRODUCT}          | 产品名称。小写，用下划线代替空格                             | unkProduct      | education_cloud_platform |
| {Version}           | 受影响版本。若未知可用 unspecified 或 all                    | all/unspecified | all                      |
| {VulnType}          | 漏洞类型。使用标准术语缩写，小写                             | -               | unauth_user_create       |
| {CVE/CNVD/CustomID} | 漏洞编号。若有 CVE/CNVD 则优先使用；若无，可自定义如 2025_znyx_01 | noId            | 2026_znyx_unauth_rce     |

所有字段使用小驼峰命名法，不同字段之间用下划线 (`_`) 分隔，允许使用的字符集合为 {a-zA-Z0-9_}。

漏洞类型常用缩写参考：

- `rce`：远程代码执行
- `sqli`：SQL 注入
- `ssrf`：服务端请求伪造
- `unauth_*`：未授权访问/操作 (如 unauth_user_create)
- `auth_bypass`：认证绕过
- `info_disclosure`：信息泄露
