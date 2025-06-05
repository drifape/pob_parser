-- Получаем путь к XML
local xmlFilePath = arg[1]
if not xmlFilePath then
    print("XML файл не передан")
    os.exit(1)
end

-- Чтение XML
local f = io.open(xmlFilePath, "r")
local xml = f:read("*a")
f:close()

-- Запускаем HeadlessWrapper
dofile("HeadlessWrapper.lua")

-- Дожидаемся инициализации PoB
while not mainObject do end

-- Загружаем билд через callback-функцию
callbackTable.loadBuildFromXML(xml, "ImportedBuild")

-- Собираем информацию о gem'ах
local gems = {}
for groupIndex, socketGroup in ipairs(build.skillsTab.socketGroupList or {}) do
    local slot = socketGroup.slot or ""
    for _, gem in ipairs(socketGroup.gemList or {}) do
        local gemData = gem.grantedEffect or {}
        table.insert(gems, {
            name = gemData.name or gem.nameSpec or "Unknown",
            level = gem.level or 0,
            quality = gem.quality or 0,
            type = gemData.support and "support" or "active",
            group = groupIndex,
            itemSlot = slot ~= "" and slot or nil
        })
    end
end

-- Выводим JSON
local json = require("dkjson")
print(json.encode(gems, { indent = false }))
