local addonName, addonTable             = ... -- luacheck: ignore addonTable

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
DejaVu.RangedRange = 40
DejaVu.MeleeRange = 5
