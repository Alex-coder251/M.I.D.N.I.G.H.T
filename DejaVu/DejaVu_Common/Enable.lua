local addonName, addonTable = ... -- luacheck: ignore addonName addonTable

local random = math.random
local insert = table.insert

local CreateFrame = CreateFrame

local DejaVu = _G["DejaVu"]
local COLOR = DejaVu.COLOR
local Cell = DejaVu.Cell
local MartixInitFuncs = DejaVu.MartixInitFuncs

local function InitFrame()
    local eventFrame = CreateFrame("Frame")

    -- x:83 y:0
    -- Purpose: display the DejaVu global enable state.
    local cell = Cell:New(83, 0)

    local function updateCell()
        cell:setCellBoolean(DejaVu.Enable == true, COLOR.GREEN, COLOR.BLACK)
    end

    updateCell()

    local fastTimeElapsed = -random()
    eventFrame:HookScript("OnUpdate", function(frame, elapsed) -- luacheck: ignore frame
        fastTimeElapsed = fastTimeElapsed + elapsed
        if fastTimeElapsed > 0.1 then
            fastTimeElapsed = fastTimeElapsed - 0.1
            updateCell()
        end
    end)
end
insert(MartixInitFuncs, InitFrame)
