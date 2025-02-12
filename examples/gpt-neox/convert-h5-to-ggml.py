import sys
import struct
import json
import numpy as np

from transformers import AutoModelForCausalLM, AutoTokenizer

if len(sys.argv) < 3:
    print("Usage: convert-h5-to-ggml.py dir-model [use-f32]\n")
    print("  ftype == 0 -> float32")
    print("  ftype == 1 -> float16")
    sys.exit(1)

# output in the same directory as the model
dir_model = sys.argv[1]
fname_out = f"{sys.argv[1]}/ggml-model.bin"

with open(f"{dir_model}/config.json", "r", encoding="utf-8") as f:
    hparams = json.load(f)

# possible data types
#   ftype == 0 -> float32
#   ftype == 1 -> float16
#
# map from ftype to string
ftype_str = ["f32", "f16"]

ftype = 1
if len(sys.argv) > 2:
    ftype = int(sys.argv[2])
    if ftype < 0 or ftype > 1:
        print(f"Invalid ftype: {ftype}")
        sys.exit(1)
    fname_out = f"{sys.argv[1]}/ggml-model-{ftype_str[ftype]}.bin"


tokenizer = AutoTokenizer.from_pretrained(dir_model)
model = AutoModelForCausalLM.from_pretrained(dir_model, low_cpu_mem_usage=True)

list_vars = model.state_dict()
for name in list_vars.keys():
    print(name, list_vars[name].shape, list_vars[name].dtype)

with open(fname_out, "wb") as fout:
    print(hparams)

    fout.write(struct.pack("i", 0x67676d6c)) # magic: ggml in hex
    fout.write(struct.pack("i", hparams["vocab_size"]))
    fout.write(struct.pack("i", hparams["max_position_embeddings"]))
    fout.write(struct.pack("i", hparams["hidden_size"]))
    fout.write(struct.pack("i", hparams["num_attention_heads"]))
    fout.write(struct.pack("i", hparams["num_hidden_layers"]))
    fout.write(struct.pack("i", int(hparams["rotary_pct"]*(hparams["hidden_size"]//hparams["num_attention_heads"]))))
    fout.write(struct.pack("i", hparams["use_parallel_residual"] if "use_parallel_residual" in hparams else True))
    fout.write(struct.pack("i", ftype))

    # TODO: temporary hack to not deal with implementing the tokenizer
    for i in range(hparams["vocab_size"]):
        text = tokenizer.decode([i]).encode('utf-8')
        fout.write(struct.pack("i", len(text)))
        fout.write(text)

    for name in list_vars.keys():
        data = list_vars[name].squeeze().numpy()
        print(f"Processing variable: {name} with shape: ", data.shape)

            # we don't need these
        if  name.endswith(".attention.masked_bias") or     \
        name.endswith(".attention.bias") or \
        name.endswith(".attention.rotary_emb.inv_freq"):
            print(f"  Skipping variable: {name}")
            continue

        n_dims = len(data.shape)

        # ftype == 0 -> float32, ftype == 1 -> float16
        ftype_cur = 0
        if ftype == 0:
            if data.dtype != np.float32:
                print("  Converting to float32")
                data = data.astype(np.float32)
                ftype_cur = 0

        elif name[-7:] == ".weight" and n_dims == 2:
            print("  Converting to float16")
            data = data.astype(np.float16)
            ftype_cur = 1
        else:
            print("  Converting to float32")
            data = data.astype(np.float32)
            ftype_cur = 0
        # header
        str = name.encode('utf-8')
        fout.write(struct.pack("iii", n_dims, len(str), ftype_cur))
        for i in range(n_dims):
            fout.write(struct.pack("i", data.shape[n_dims - 1 - i]))
        fout.write(str)

        # data
        data.tofile(fout)

print(f"Done. Output file: {fname_out}")
print("")
