require 'torch'
require 'nn'
-- require 'io'

require 'LanguageModel'

local cmd = torch.CmdLine()
cmd:option('-checkpoint', 'cv/checkpoint_4000.t7')
cmd:option('-text', '')
cmd:option('-temperature', 1)
cmd:option('-batch', 0)
local opt = cmd:parse(arg)

local checkpoint = torch.load(opt.checkpoint)
local model = checkpoint.model

model:evaluate()

if opt.batch == 0 then
	local score = model:get_text_score(opt.text, opt.temperature)
	print(score)
else
    local file = io.open("temp.txt","rb")
    -- local debug_file = io.open("debug.txt","w")
    if not file then return nil end
    local best_score = 0
    local best_idx = 0
    local cur_idx = 0
    while true do
        local line = file:read()
        if line == nil then break end
        if string.sub(line,1,5) == "=====" then
            io.write(best_idx,',')
            cur_idx = 0
            best_score = 0
            best_idx = 0
        else
            local score = model:get_text_score(line, opt.temperature)
            -- debug_file:write(score,' ',string.len(line),' ',line,'\n')
            if score > best_score then
                best_score = score
                best_idx = cur_idx
            end
            cur_idx = cur_idx + 1
        end
    end
end