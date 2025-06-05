local xmlFilePath = arg[1]
if not xmlFilePath then
    print("XML файл не передан")
    os.exit(1)
end

local f = io.open(xmlFilePath, "r")
local xml = f:read("*a")
f:close()

dofile("/pob/src/HeadlessWrapper.lua")
loadBuildFromXML(xml, "ImportedBuild")

local gems = {}
for groupIndex, socketGroup in ipairs(build.skillsTab.socketGroupList) do
    local slot = socketGroup.slot or ""
    for _, gem in ipairs(socketGroup.gemList) do
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

local json = require("dkjson")
print(json.encode(gems, { indent = false }))
