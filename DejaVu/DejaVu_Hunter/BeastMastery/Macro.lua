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
insert(macroList, { title = "误导", key = "ALT-NUMPAD1", text = "/cast [target=focus,help,nodead][target=pet,exists,nodead][] 误导" })
insert(macroList, { title = "召唤宠物", key = "ALT-NUMPAD2", text = "/cast 召唤宠物" })
insert(macroList, { title = "复活宠物", key = "ALT-NUMPAD3", text = "/cast 复活宠物" })
insert(macroList, { title = "target杀戮命令", key = "ALT-NUMPAD4", text = "/cast [@target] 杀戮命令" })
insert(macroList, { title = "target狂野怒火", key = "ALT-NUMPAD5", text = "/cast [@target] 狂野怒火" })
insert(macroList, { title = "target狂野鞭笞", key = "ALT-NUMPAD6", text = "/cast [@target] 狂野鞭笞" })
insert(macroList, { title = "target猎人印记", key = "ALT-NUMPAD7", text = "/cast [@target] 猎人印记" })
insert(macroList, { title = "target宁神射击", key = "ALT-NUMPAD8", text = "/cast [@target] 宁神射击" })
insert(macroList, { title = "target反制射击", key = "ALT-NUMPAD9", text = "/cast [@target] 反制射击" })
insert(macroList, { title = "focus反制射击", key = "ALT-NUMPAD0", text = "/cast [@focus] 反制射击" })
insert(macroList, { title = "target眼镜蛇射击", key = "SHIFT-NUMPAD1", text = "/cast [@target] 眼镜蛇射击" })
insert(macroList, { title = "focus宁神射击", key = "SHIFT-NUMPAD2", text = "/cast [@focus] 宁神射击" })
insert(macroList, { title = "target倒刺射击", key = "SHIFT-NUMPAD3", text = "/cast [@target] 倒刺射击" })

for macroIndex, macro in pairs(macroList) do -- luacheck: ignore macroIndex
    local buttonName = addonName .. "Button" .. macro.title
    local frame = CreateFrame("Button", buttonName, UIParent, "SecureActionButtonTemplate")
    frame:SetAttribute("type", "macro")
    frame:SetAttribute("macrotext", macro.text)
    frame:RegisterForClicks("AnyDown", "AnyUp")
    SetOverrideBindingClick(frame, true, macro.key, buttonName)
    print("RegMacro[" .. macro.title .. "] > " .. macro.key .. " > " .. macro.text)
end
