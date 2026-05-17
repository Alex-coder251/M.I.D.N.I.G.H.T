local addonName, addonTable             = ... -- luacheck: ignore addonTable

local insert                            = table.insert
local pairs                             = pairs

local CreateFrame                       = CreateFrame
local SetOverrideBindingClick           = SetOverrideBindingClick
local UnitClass                         = UnitClass
local GetSpecialization                 = GetSpecialization

local className, classFilename, classId = UnitClass("player") -- luacheck: ignore className classId
local currentSpec                       = GetSpecialization()
if classFilename ~= "HUNTER" then
    C_AddOns.DisableAddOn(addonName)
    return
end
if currentSpec ~= 1 then return end

local macroList = {}
insert(macroList, { title = "reloadUI", key = "CTRL-F12", text = "/reload" })

for macroIndex, macro in pairs(macroList) do -- luacheck: ignore macroIndex
    local buttonName = addonName .. "Button" .. macro.title
    local frame = CreateFrame("Button", buttonName, UIParent, "SecureActionButtonTemplate")
    frame:SetAttribute("type", "macro")
    frame:SetAttribute("macrotext", macro.text)
    frame:RegisterForClicks("AnyDown", "AnyUp")
    SetOverrideBindingClick(frame, true, macro.key, buttonName)
    print("RegMacro[" .. macro.title .. "] > " .. macro.key .. " > " .. macro.text)
end
