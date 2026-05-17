local addonName, addonTable             = ... -- luacheck: ignore addonTable

local insert                            = table.insert
local random                            = math.random

local CreateFrame                       = CreateFrame
local UnitPower                         = UnitPower
local UnitPowerMax                      = UnitPowerMax
local UnitClass                         = UnitClass
local GetSpecialization                 = GetSpecialization
local GetPlayerAuraBySpellID            = C_UnitAuras.GetPlayerAuraBySpellID

local className, classFilename, classId = UnitClass("player") -- luacheck: ignore className classId
local currentSpec                       = GetSpecialization()
if classFilename ~= "HUNTER" then
    C_AddOns.DisableAddOn(addonName)
    return
end
if currentSpec ~= 1 then return end

local DejaVu = _G["DejaVu"]
local Cell = DejaVu.Cell
local MartixInitFuncs = DejaVu.MartixInitFuncs

local FOCUS_POWER_TYPE = Enum.PowerType.Focus
local FRENZY_BUFF_ID = 272790

local function InitFrame()
    local eventFrame = CreateFrame("Frame")

    local cells = {
        -- x:55 y:13
        -- Purpose: display Beast Mastery hunter focus, using the same power type SenseiClassResourceBar uses for hunters.
        Focus = Cell:New(55, 13),
        -- x:56 y:13
        -- Purpose: display pet Frenzy stacks from Barbed Shot.
        Frenzy = Cell:New(56, 13)
    }

    local function UpdateFocus()
        local current = UnitPower("player", FOCUS_POWER_TYPE)
        local max = UnitPowerMax("player", FOCUS_POWER_TYPE)
        if max and max > 0 then
            cells.Focus:setCellRGBA(current / max)
        else
            cells.Focus:setCellRGBA(0)
        end
    end

    local function UpdateFrenzy()
        local auraData = GetPlayerAuraBySpellID(FRENZY_BUFF_ID)
        local applications = auraData and auraData.applications or 0
        cells.Frenzy:setCellRGBA(applications * 51 / 255)
    end

    local fastTimeElapsed = -random()
    eventFrame:HookScript("OnUpdate", function(frame, elapsed) -- luacheck: ignore frame
        fastTimeElapsed = fastTimeElapsed + elapsed
        if fastTimeElapsed > 0.1 then
            fastTimeElapsed = fastTimeElapsed - 0.1
            UpdateFocus()
            UpdateFrenzy()
        end
    end)

    -- Purpose: refresh Beast Mastery focus when player power changes.
    eventFrame:RegisterUnitEvent("UNIT_POWER_FREQUENT", "player")
    -- Purpose: refresh pet Frenzy stacks when player aura data changes.
    eventFrame:RegisterUnitEvent("UNIT_AURA", "player")
    -- Purpose: refresh both cells after login/loading transitions.
    eventFrame:RegisterEvent("PLAYER_ENTERING_WORLD")

    eventFrame:SetScript("OnEvent", function(self, event, unit) -- luacheck: ignore self event unit
        UpdateFocus()
        UpdateFrenzy()
    end)
end
insert(MartixInitFuncs, InitFrame)
