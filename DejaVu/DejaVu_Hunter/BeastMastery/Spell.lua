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

insert(cooldownSpells, { spellID = 34026, name = "Kill Command" })
insert(cooldownSpells, { spellID = 217200, name = "Barbed Shot" })
insert(cooldownSpells, { spellID = 19574, name = "Bestial Wrath" })
insert(cooldownSpells, { spellID = 193530, name = "Aspect of the Wild" })
insert(cooldownSpells, { spellID = 147362, name = "Counter Shot" })
insert(cooldownSpells, { spellID = 109304, name = "Exhilaration" })
