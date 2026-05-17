local addonName, addonTable             = ... -- luacheck: ignore addonTable

local insert                            = table.insert

local UnitClass                         = UnitClass
local GetSpecialization                 = GetSpecialization

local className, classFilename, classId = UnitClass("player") -- luacheck: ignore className classId
local currentSpec                       = GetSpecialization()
if classFilename ~= "HUNTER" then
    C_AddOns.DisableAddOn(addonName)
    return
end
if currentSpec ~= 1 then return end

local DejaVu = _G["DejaVu"]
local cooldownSpells = DejaVu.cooldownSpells

insert(cooldownSpells, { spellID = 34026, name = "杀戮命令" })
insert(cooldownSpells, { spellID = 217200, name = "倒刺射击" })
insert(cooldownSpells, { spellID = 19574, name = "狂野怒火" })
insert(cooldownSpells, { spellID = 193530, name = "野性守护" })
insert(cooldownSpells, { spellID = 147362, name = "反制射击" })
insert(cooldownSpells, { spellID = 109304, name = "意气风发" })
insert(cooldownSpells, { spellID = 1264359, name = "狂野鞭笞" })
insert(cooldownSpells, { spellID = 257284, name = "猎人印记" })
insert(cooldownSpells, { spellID = 34477, name = "误导" })
insert(cooldownSpells, { spellID = 19801, name = "宁神射击" })
insert(cooldownSpells, { spellID = 883, name = "召唤宠物" })
insert(cooldownSpells, { spellID = 982, name = "复活宠物" })

