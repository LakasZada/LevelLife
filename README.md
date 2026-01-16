# LevelLife

**LevelLife** is a gamified productivity and life-management game inspired by RPGs and roguelites.  
It turns real-life tasks into quests, skills into XP bars, and consistency into long-term progression.

Built with **Python + Pygame**, LevelLife runs on **PC** and **Android (via Pydroid 3)**.

---

## 🎮 Core Concept

LevelLife is a **persistent RPG-style to-do system** where:

- Tasks grant **skill-specific XP**
- Missing tasks costs **lives**
- Accessories and characters grant **XP boosts**
- Rebirth converts XP into **permanent progression**
- Progress carries forward across deaths

It blends productivity, progression, and light punishment/reward systems into a single loop.

---

## 🧠 Core Systems

### 🧩 Skills
- Programming  
- Fitness  
- Social  
- School  
- Other  

Each skill has:
- Its own XP
- Boost modifiers
- Visual-only XP bars (boosts affect gain, not display)

---

### ✅ Tasks
- Assigned to days of the week (1–7)
- Linked to a skill
- Optional timer for bonus XP
- Missing a task → lose a life

---

### 💀 Lives & Rebirth
- Missing tasks reduces lives
- Reaching 0 lives triggers **death**
- Death/Rebirth:
  - Resets XP & levels
  - Converts XP into **rebirth points**
  - Permanent XP boosts are selected

---

### 🎒 Accessories & Characters
- Accessories boost skill XP
- Displayed as **text descriptions** in the XP overlay
- Characters represent the player visually
- Unlock via milestones or progression

---

### 🌐 Social (Optional / Expandable)
- Friends list
- Teams
- Shared task completion bonuses
- Social XP tracking

---

## 🖥 UI Overview

**Main Screen**
- Top bar: titles, character (center), friends
- Overall XP bar (click → Skill XP Overlay)
- Bottom hotbar:
  - Slots 1–7: days of the week
  - Slot 8: menu

**Skill XP Overlay**
- Skill XP bars
- Rebirth boosts
- Accessory descriptions

**Menu Screens**
- Bonus tasks
- Shops
- Rebirth / prestige
- Teams & chat
- Leaderboards
- Settings

---

## 📁 Project Structure

