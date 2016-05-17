require 'torch'
require 'nn'

require 'LanguageModel'

local cmd = torch.CmdLine()
cmd:option('-checkpoint', 'cv/checkpoint_4000.t7')
cmd:option('-text', '')
cmd:option('-temperature', 1)
local opt = cmd:parse(arg)

local checkpoint = torch.load(opt.checkpoint)
local model = checkpoint.model

model:evaluate()

local score = model:get_text_score(opt)
print(score)
