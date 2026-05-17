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
local Config = DejaVu.Config
local ConfigRows = DejaVu.ConfigRows
local Cell = DejaVu.Cell
local MartixInitFuncs = DejaVu.MartixInitFuncs

do
    local bm_interrupt_mode = Config("bm_interrupt_mode")
    insert(ConfigRows, {
        type = "combo",
        key = "bm_interrupt_mode",
        name = "BM interrupt mode",
        tooltip = "Select Beast Mastery interrupt display mode",
        default_value = "blacklist",
        options = {
            { k = "blacklist", v = "Blacklist" },
            { k = "all", v = "All" }
        },
        bind_config = bm_interrupt_mode,
    })

    local function InitFrame()
        -- x:55 y:12
        -- Purpose: display Beast Mastery interrupt mode config.
        local bm_interrupt_mode_cell = Cell:New(55, 12)

        local function set_bm_interrupt_mode(value)
            if value == "blacklist" then
                bm_interrupt_mode_cell:setCellRGBA(255 / 255)
            else
                bm_interrupt_mode_cell:setCellRGBA(127 / 255)
            end
        end

        bm_interrupt_mode:register_callback(set_bm_interrupt_mode)
        set_bm_interrupt_mode(bm_interrupt_mode:get_value())
    end
    insert(MartixInitFuncs, InitFrame)
end
