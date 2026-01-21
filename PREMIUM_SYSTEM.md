# 🎁 PREMIUM SYSTEM - USER DOCUMENTATION

## Overview
Premium system add kiya gya hai jo users ko token ads dekhne se exempt karta hai!

---

## 📌 **ADMIN COMMANDS**

### 1. `/premium <userID> <days>`
User ko premium status deta hai.

**Usage Example:**
```
/premium 123456789 30
```

**What it does:**
- User ko 30 days ke liye premium status deta hai
- Premium users ko token ads verification skip ho jayega
- User permanently access pai rahega (ads nahi dekh payega)

**Response:**
```
✅ ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!

👤 ᴜsᴇʀ ɪᴅ: 123456789
📅 ᴅᴜʀᴀᴛɪᴏɴ: 30 ᴅᴀʏs
🎁 ᴘᴇʀᴋ: ɴᴏ ᴛᴏᴋᴇɴ ᴀᴅs ʀᴇqᴜɪʀᴇᴅ
```

---

### 2. `/remove <userID>`
User ka premium status remove karta hai.

**Usage Example:**
```
/remove 123456789
```

**What it does:**
- User ka premium status hata deta hai
- User wapas regular user ban jaata hai
- Ab use token ads dekh sakte honge

**Response:**
```
✅ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!

👤 ᴜsᴇʀ ɪᴅ: 123456789
📌 sᴛᴀᴛᴜs: ʀᴇɢᴜʟᴀʀ ᴜsᴇʀ
```

---

## 🛠️ **TECHNICAL DETAILS**

### Database Changes
Database mein naya collection add hua:
- **Collection Name:** `premium_users`
- **Fields:**
  - `_id` → User ID
  - `expiry_date` → Premium expiry date
  - `added_on` → Jab premium add hua

### Code Changes

#### 1. **Database Functions** (`databases/database.py`)
```python
# Premium user set karna
await db.set_premium_user(user_id, days)

# Check if user premium hai
is_premium = await db.is_premium_user(user_id)

# Premium remove karna
await db.remove_premium_user(user_id)

# Premium user info
info = await db.get_premium_user_info(user_id)
```

#### 2. **Bot Commands** (`plugins/bot_cmd.py`)
- `/premium <userID> <days>` command add hua
- `/remove <userID>` command add hua

#### 3. **Token Verification Logic** (`plugins/start.py`)
```python
# Premium users ko automatic verify kia jata hai
is_premium = await db.is_premium_user(id)
if is_premium:
    # User verified manaya jata hai - ads skip ho jate hain
    verify_status['is_verified'] = True
```

---

## ✅ **HOW IT WORKS**

### User Flow:
1. **Regular User:**
   - `/start` → Token required → Ads show → Access milta hai

2. **Premium User:**
   - `/start` → Directly access (No ads/token required)
   - Premium expiry tak ye status rahega
   - Expiry ke baad automatically regular user ban jaata hai

### Admin Flow:
1. Admin `/premium 123456789 30` run karta hai
2. User premium ban jata hai 30 days ke liye
3. Jab user `/start` karta hai, wo ads skip kar deta hai
4. 30 days baad premium auto-expire ho jaata hai
5. Admin `/remove 123456789` se manually bhi remove kar sakta hai

---

## 🎯 **FEATURES**

✅ **Premium Status Management**
- Set premium with days duration
- Auto-expire after given days
- Manual removal option

✅ **Seamless Integration**
- Existing code unchanged
- Works with current token system
- Database-backed persistence

✅ **Admin Friendly**
- Simple commands
- Clear feedback messages
- Bilingual support (Hinglish UI)

---

## 📊 **EXAMPLES**

### Add Premium for 7 Days:
```
/premium 987654321 7
```

### Add Premium for 30 Days:
```
/premium 123456789 30
```

### Add Premium for 365 Days (1 Year):
```
/premium 111222333 365
```

### Remove Premium:
```
/remove 987654321
```

---

## ⚠️ **IMPORTANT NOTES**

1. **Days must be > 0** - Negative ya 0 days accept nahi hote
2. **Auto-Expiry** - Expired premium automatically remove ho jata hai
3. **Admin Only** - Ye commands sirf admins use kar sakte hain
4. **No Ads for Premium** - Premium users ko token verification skip ho jata hai

---

## 🔧 **DATABASE QUERIES**

### Check if premium:
```python
is_premium = await db.is_premium_user(123456789)
# Returns: True/False
```

### Get all premium users:
```python
premium_users = await db.get_all_premium_users()
# Returns: [user_id1, user_id2, ...]
```

### Get premium info:
```python
info = await db.get_premium_user_info(123456789)
# Returns: {'user_id': 123456789, 'expiry_date': datetime, 'added_on': datetime}
```

---

## 🎉 **SUMMARY**

✨ Full premium system add hua!
- Existing code preserved
- Clean integration
- Database-backed
- Production ready

**Abhi use kar sakte ho! 🚀**
