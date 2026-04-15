# NPA-guy Heartbeat Tasks

## [1]. Track LED red case พ.97/2567 (Songkhla)
- When: Every heartbeat / daily review cycle
- Priority: HIGH
- Instructions: Track LED red code `พ.97/2567` continuously even if original LED asset ID changes after delist/repricing. Current known record: asset_id `1869319`, LED_สงขลา, เมืองสงขลา, เขารูปช้าง, ที่ดินพร้อมสิ่งปลูกสร้าง, 18.6 ตร.ว., 6 rounds unsold as of 2026-04-07. On each review: search by `case_number='พ.97/2567'`, deed `83776`, court `จังหวัดสงขลา`, plaintiff `ธนาคารทิสโก้ จำกัด (มหาชน)`, defendant `ห้างหุ้นส่วนจำกัดสงขลาท็อปอัพ ที่ 1 กับพวก`; detect relist/new asset_id/new price; report any price reset, relist, status change, or next auction update immediately.

<!-- Task format:
## [N]. [Task Name]
- When: [schedule]
- Priority: [LOW/MEDIUM/HIGH]
- Instructions: [what to do]
-->
