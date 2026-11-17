---
name: "handoff-other-llm"
description: "สรุปสถานะโปรเจคและ session เป็น HANDOFF.md ให้ LLM/coding agent ตัวอื่น (Codex, Antigravity, Cursor, Gemini CLI) ทำงานต่อได้ทันที ใช้ทุกครั้งที่ผู้ใช้ต้องการส่งต่องานให้ LLM/agent อื่น, ขอสรุป session เพื่อทำต่อที่อื่น, หรือพูดว่า \"handoff\", \"hand off\", \"ส่งต่องาน\", \"สรุปให้ Codex ทำต่อ\", \"ย้ายไปทำต่อใน Cursor\" แม้ไม่ได้เอ่ยชื่อ skill"
---

# Handoff ให้ LLM/agent ตัวอื่น

เขียน `HANDOFF.md` ที่ root ของ repo ให้ coding agent ตัวอื่นอ่านแล้วทำงานต่อได้ทันที

ผู้อ่านคือ agent ที่ **ไม่เห็นบทสนทนานี้ และถามกลับไม่ได้** ทุกอย่างที่มันต้องรู้ต้องอยู่ในไฟล์ และทุกอย่างที่เขียนผิดมันจะเชื่อตาม กฎทั้งหมดด้านล่างมาจากข้อเท็จจริงสองข้อนี้

## Argument

`$ARGUMENTS` (ไม่บังคับ) อาจมีชื่อ LLM ปลายทาง และ/หรือขอบเขตงานที่อยากให้เน้น

- มีชื่อ LLM ปลายทาง: ใส่ชื่อนั้นใน kickoff prompt และหัวเอกสาร
- มีขอบเขตงาน: ให้ Next steps, In progress และ Files to read first เน้นขอบเขตนั้น งานนอกขอบเขตย่อเหลือบรรทัดเดียว แต่ Project overview และ How to run ยังต้องครบ
- ว่าง: เขียนครอบคลุมทั้ง session สำหรับ agent ทั่วไป

## ข้อห้ามระหว่างทำ handoff

อ่านได้ทุกอย่าง แต่เขียนได้เฉพาะไฟล์ handoff (`HANDOFF.md`, `docs/handoff/*`, และ `AGENTS.md` เมื่อผู้ใช้ตอบตกลง) ไม่แก้ code, ไม่ stage, ไม่ commit, ไม่ stash, ไม่สลับ branch เพราะเอกสารต้องบรรยายสถานะที่เป็นอยู่จริง ถ้าแก้ระหว่างทาง สิ่งที่เขียนจะไม่ตรงกับ repo

## ขั้นตอน

### 1. รวบรวมข้อมูลจากของจริง

รันจาก root ของ repo:

```bash
if git rev-parse --show-toplevel 2>/dev/null; then
  git status --short
  git branch --show-current
  git log --oneline -15
  git diff --stat            # unstaged
  git diff --cached --stat   # staged
else
  echo "NOT A GIT REPO: $(pwd)"
fi
```

ต้องเช็ก `git rev-parse` ก่อนเสมอ เพราะนอก git repo คำสั่งอย่าง `git diff --stat` จะพ่นข้อความ usage ยาวหลายสิบบรรทัดที่ไม่มีประโยชน์ ถ้าไม่ใช่ git repo ให้ใช้ directory ปัจจุบันเป็น root ระบุในบรรทัดหัวเอกสารและหัวข้อ Current session ว่า "ไม่ใช่ git repo" และข้าม commit hash

อ่านไฟล์เหล่านี้ถ้ามี:

- `README*`, `CLAUDE.md`, `AGENTS.md`
- package manifest: `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pubspec.yaml`, `Makefile` ฯลฯ
- โครงสร้างโฟลเดอร์ลึก 2 ระดับ ข้าม `.git`, `node_modules`, `.venv`, `dist`, `build`
- ชื่อ environment variable จาก `.env.example` หรือจาก code ที่อ่านค่า env ถ้ามีแต่ `.env` ให้ดึงเฉพาะชื่อ key (`cut -d= -f1 .env`) ห้ามอ่านค่าเข้ามาในบริบท

**ถ้าโค้ดอยู่นอก root หรือกระจายหลาย repo:** ดูว่าสคริปต์รัน, manifest (workspaces, submodule) หรือเอกสารใน root ชี้ไปที่ repo หรือโฟลเดอร์พี่น้องหรือไม่ (เช่น `cd ../backend`, path แบบ absolute ไปนอก root) ถ้าชี้ ของพวกนั้นคือส่วนหนึ่งของโปรเจค agent ปลายทางต้องรู้สถานะของมันด้วย

- repo ที่เข้าถึงได้: รันบล็อก git ชุดเดียวกันด้วย `git -C <path>` (อ่านอย่างเดียว) แล้วรายงานแยกตาม repo
- repo ที่เข้าถึงไม่ได้: อย่าเดาสถานะ ให้บอกตรงๆ ว่าไม่ได้ตรวจ และถ้ามีเอกสารที่เล่าสถานะของมันไว้ ให้คัดมาพร้อมชื่อไฟล์ต้นทางและวันที่ แล้วติด `[unverified]`
- ระบุในหัวเอกสารว่า path ทั้งหมด relative กับ directory ไหน

จากบทสนทนาใน session นี้ ดึง: เป้าหมาย, สิ่งที่ทำไปแล้ว, การตัดสินใจและเหตุผล, สิ่งที่ลองแล้วไม่ได้ผล, todo ที่ค้าง

ถ้า session นี้เพิ่งเริ่มและไม่มีบทสนทนาเกี่ยวกับงาน ให้เขียนตรงๆ ว่า "ไม่มีบริบทจาก session ก่อนหน้า สรุปจาก repo เท่านั้น" อย่าแต่งเป้าหมายหรือการตัดสินใจขึ้นมาจาก commit message

### 2. เก็บ HANDOFF.md เดิม

```bash
[ -f HANDOFF.md ] && mkdir -p docs/handoff && mv -n HANDOFF.md "docs/handoff/HANDOFF-$(date +%Y%m%d-%H%M).md"
```

### 3. เขียน HANDOFF.md

ใช้โครงสร้างนี้ครบทุกหัวข้อตามลำดับ หัวข้อไหนไม่มีข้อมูลให้เขียน "ไม่มี" อย่าลบหัวข้อ เพราะ agent ปลายทางจะได้รู้ว่าตรวจแล้วว่าไม่มี ไม่ใช่ลืมเขียน

```markdown
# HANDOFF

> สร้างเมื่อ <YYYY-MM-DD HH:MM> | branch `<branch>` | HEAD `<short-hash>` | ปลายทาง: <LLM หรือ "agent ทั่วไป">
> เอกสารนี้เขียนให้ coding agent ที่ไม่เห็นบทสนทนาก่อนหน้า ข้อความที่ติดป้าย [unverified] คือข้อสันนิษฐาน ให้ตรวจก่อนเชื่อ
> ขอบเขตที่ตรวจ: <repo/โฟลเดอร์ที่เปิดอ่านจริง> | ไม่ได้ตรวจ: <repo/โฟลเดอร์ที่ถูกอ้างถึงแต่ไม่ได้เปิด หรือ "ไม่มี"> | path relative กับ `<directory>`

## 1. TL;DR
3–5 บรรทัด: โปรเจคคืออะไร, ตอนนี้อยู่ตรงไหน, ต้องทำอะไรต่อทันที

## 2. Project overview
จุดประสงค์, ผู้ใช้, tech stack, โครงสร้างโฟลเดอร์สำคัญ

## 3. How to run
คำสั่ง install / dev / test / build / lint พร้อมที่มาของแต่ละคำสั่ง (ไฟล์ไหน) และบอกว่าคำสั่งไหนรันผ่านจริงใน session นี้ ตามด้วยตาราง environment variable (ชื่อ + ใช้ทำอะไร ไม่มีค่า)

## 4. Current session
เป้าหมายของ session นี้ และ branch ที่ทำงานอยู่ (ถ้ามีหลาย repo ให้ระบุ branch และ HEAD ต่อ repo)

## 5. Done
งานที่เสร็จ พร้อม path ไฟล์และ commit hash

## 6. In progress
งานค้างกลางทาง: ไฟล์ไหน แก้ถึงไหน อะไรยังพัง และรายการ uncommitted changes (staged / unstaged / untracked) แยกตาม repo ถ้ามีหลาย repo

## 7. Next steps
เรียงตามความสำคัญ แต่ละข้อมี:
1. **<สิ่งที่ต้องทำ>**
   - ไฟล์: `path/a`, `path/b`
   - เสร็จเมื่อ: <acceptance criteria ที่ตรวจได้ เช่น คำสั่งที่ต้องผ่าน>

## 8. Decisions & rationale
การตัดสินใจเชิงออกแบบที่ทำไปแล้ว + เหตุผล + ทางเลือกที่ตัดทิ้ง

## 9. Gotchas
สิ่งที่ลองแล้วไม่ได้ผล, bug ที่รู้อยู่, ข้อจำกัด, สิ่งที่ห้ามแตะ

## 10. Open questions
เรื่องที่ต้องรอผู้ใช้ตัดสินใจ agent ปลายทางไม่ควรตัดสินใจเอง

## 11. Files to read first
5–10 ไฟล์ตามลำดับที่ควรอ่าน พร้อมเหตุผลสั้นๆ ว่าทำไม
```

### 4. AGENTS.md

- มีอยู่แล้ว: อ้างถึงใน Project overview และ Files to read first แทนการคัดลอกเนื้อหามาซ้ำ
- ยังไม่มี: หลังเขียน HANDOFF.md เสร็จ ถามผู้ใช้ว่าต้องการสร้างด้วยหรือไม่ (Codex และ agent หลายตัวอ่านไฟล์นี้อัตโนมัติ) สร้างเมื่อผู้ใช้ตอบตกลงเท่านั้น และใส่เฉพาะสิ่งที่คงที่ข้าม session: คำสั่ง run/test, convention, ข้อห้าม สถานะงานอยู่ใน HANDOFF.md

### 5. ตรวจก่อนส่ง

```bash
wc -l HANDOFF.md
grep -nEi '(api[_-]?key|secret|token|passw(or)?d|bearer)[[:space:]]*[:=][[:space:]]*[^[:space:]]{8,}|sk-[A-Za-z0-9_-]{16,}|gh[pous]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN' HANDOFF.md
grep -nEi 'ตามที่คุย|เมื่อกี้|ก่อนหน้านี้ในแชท|as discussed|slash command|subagent|skill|hook' HANDOFF.md
git status --short
```

- `wc -l` เกินประมาณ 300 บรรทัด: ตัดรายละเอียดที่อ่านจากไฟล์ใน repo ได้เอง เหลือแค่ path
- grep ตัวแรกเจอ: เปิดดูบรรทัดนั้นก่อน ถ้าเป็นค่าจริงให้ลบออกเหลือแค่ชื่อตัวแปร ถ้าเป็น placeholder เช่น `<token>`, `$VAR`, `xxx`, `your-key-here` ถือว่าผ่าน (pattern นี้ตั้งใจจับกว้างไว้ก่อน จึงมี false positive ได้)
- grep ตัวที่สองเจอ: อ่านบรรทัดนั้นแล้วเขียนใหม่ให้ self-contained และ tool-agnostic (คำอย่าง skill หรือ hook อาจเป็นศัพท์ของโปรเจคเองก็ได้ ใช้วิจารณญาณ)
- `git status` ต้องต่างจากตอนเริ่มเฉพาะ `HANDOFF.md`, `docs/handoff/` และ `AGENTS.md` (ถ้าสร้าง) ถ้าไม่ใช่ git repo ให้ข้ามบรรทัดนี้

### 6. แสดง kickoff prompt

ปิดท้ายใน chat ด้วย path ของไฟล์ที่เขียน และ kickoff prompt สั้นๆ ใน code block ให้ผู้ใช้ copy ไปวางใน LLM ปลายทาง ชี้ไปที่ข้อแรกของ Next steps เช่น:

```text
อ่าน HANDOFF.md ที่ root ของ repo ให้จบก่อน แล้วอ่านไฟล์ในหัวข้อ "Files to read first" ตามลำดับ
จากนั้นทำต่อจากหัวข้อ "Next steps" ข้อ 1 (<ชื่องาน>) จนผ่านเกณฑ์ "เสร็จเมื่อ"
อย่ารื้อสิ่งที่อยู่ใน "Decisions & rationale" และถ้าเจอเรื่องใน "Open questions" ให้หยุดถามผู้ใช้
```

## กฎการเขียน

- **Tool-agnostic**: agent ปลายทางไม่มี skills, subagents, slash commands หรือ hooks ของ Claude Code ถ้างานเดิมพึ่งสิ่งเหล่านี้ ให้อธิบายเป็นขั้นตอนทั่วไปหรือคำสั่ง shell ที่ agent ไหนก็รันได้
- **Self-contained**: ห้ามเขียน "ตามที่คุยกัน", "ไฟล์ที่แก้เมื่อกี้", "วิธีที่สอง" ให้ระบุ path, ชื่อ function, ชื่อ branch, commit hash ทุกครั้ง
- **ตรวจสอบแล้ว กับ สันนิษฐาน**: agent ปลายทางต้องรู้ว่าบรรทัดไหนเชื่อได้เลยและบรรทัดไหนต้องตรวจก่อนลงมือ
  - ตรวจสอบแล้ว (เขียนได้ตรงๆ): สิ่งที่รันจริงใน session นี้และเห็นผล หรืออ่านจากไฟล์ที่เป็นต้นทางของข้อเท็จจริงนั้นโดยตรง คำสั่งที่เห็นใน manifest, สคริปต์ หรือ CI config นับว่าตรวจแล้วว่า "มีอยู่" ให้ระบุที่มา เช่น "(ที่มา: package.json)" ส่วนคำว่า "รันผ่าน" ใช้ได้เฉพาะเมื่อรันจริงแล้วผ่าน
  - `[unverified]` ท้ายบรรทัด: สิ่งที่อนุมาน, สิ่งที่จำได้จากบทสนทนาแต่ไม่ได้ตรวจซ้ำ, คำสั่งที่เดาเองโดยไม่เห็นในไฟล์ไหน และข้อมูลมือสอง คือเอกสารที่เล่าสถานะของสิ่งอื่นซึ่งไม่ได้เปิดดูของจริง (handoff หรือบันทึกเก่า, README ที่บอกว่า test ผ่าน, สถานะของ repo อื่น) กรณีมือสองให้บอกชื่อไฟล์ต้นทางและวันที่ด้วย เพราะสถานะอาจเปลี่ยนไปแล้ว
- **ไม่มีความลับและข้อมูลส่วนบุคคล**: ห้ามใส่ secret, API key, token, password, connection string ที่มี credential และห้ามใส่ข้อมูลส่วนบุคคลหรือข้อมูลผู้ป่วย (ชื่อ, เลขบัตร, HN, แถวข้อมูลจริงจาก dataset) ถ้าต้องอธิบายข้อมูล ให้บอกแค่ schema และชื่อ column เอกสารนี้จะถูกวางใน LLM ของผู้ให้บริการรายอื่นและอาจถูก commit
- **ภาษา**: ใช้ภาษาเดียวกับเอกสารหลักของโปรเจค (README) ค่าเริ่มต้นคือไทย คงศัพท์เทคนิค, path, คำสั่ง และชื่อหัวข้อเป็นอังกฤษ
- **กระชับ**: ไม่เกินประมาณ 300 บรรทัด ใช้ bullet และ path แทนการคัดลอก code ยาวๆ เพราะ agent ปลายทางเปิดไฟล์อ่านเองได้
- **Next steps ต้องลงมือได้**: ถ้าข้อไหนเขียน acceptance criteria ไม่ได้ แปลว่ายังไม่ชัดพอ ให้ย้ายไป Open questions