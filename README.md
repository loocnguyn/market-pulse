# market-pulse

Nhật ký giá crypto và tỷ giá USD/VND, tự ghi bằng GitHub Actions.

Cứ khoảng 3 tiếng, workflow lấy giá BTC, ETH, SOL từ CoinGecko và tỷ giá USD→VND từ open.er-api.com, thêm một dòng vào [`data/prices.csv`](data/prices.csv) rồi cập nhật bảng bên dưới. Một số lượt được bỏ qua ngẫu nhiên và mỗi lượt chạy lệch vài phút.

## Mới nhất

<!-- pulse:start -->
_Cập nhật lần cuối: 21/10/2026 11:56 (giờ VN) · 4 lần ghi_

| Đồng | Giá | 24h | Gần đây |
|---|---:|---:|---|
| BTC | $82,697 | +0.83% | `▃▁█▇` |
| ETH | $2,442 | +1.27% | `▃▁█▇` |
| SOL | $105.75 | +0.54% | `▄▁█▆` |

1 USD ≈ **25,846 VND**
<!-- pulse:end -->

## Chạy ở máy

```bash
python scripts/snapshot.py
```

Chỉ dùng thư viện chuẩn của Python 3, không cần cài gì thêm.

## Dữ liệu

`data/prices.csv`: `time_utc, btc_usd, eth_usd, sol_usd, usd_vnd`

Dữ liệu chỉ để tham khảo, không phải lời khuyên đầu tư.
