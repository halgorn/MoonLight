# MoonLight AI Library - Guia Completo

## Visão Geral

A biblioteca AI do MoonLight fornece abstrações de alto nível para Machine Learning e IA Generativa, compatível com PyTorch e TensorFlow.

## Instalação

```bash
pip install torch torchvision transformers
```

## Módulos

### 1. ai.tensor - Operações com Tensors

```moonlight
from ai.tensor import tensor, zeros, ones, randn

# Criar tensors
x = tensor([1.0, 2.0, 3.0], requires_grad=True)
y = zeros([10], requires_grad=False)
z = randn([5, 5], requires_grad=True)

# Operações
result = matmul(x, y)
s = sum(z, dim=0)
m = mean(z, dim=1)

# GPU
x_gpu = x.cuda()
x_cpu = x_gpu.cpu()

# Backpropagation
loss = sum(x * x, 0)
loss.backward()
print(x.grad)
```

### 2. ai.nn - Neural Network Layers

#### Linear (Fully Connected)
```moonlight
from ai.nn import Linear

layer = Linear(in_features=784, out_features=128, bias=True)
output = layer.forward(input)
```

#### Conv2D (Convolutional)
```moonlight
from ai.nn import Conv2D

conv = Conv2D(
    in_channels=3,
    out_channels=64,
    kernel_size=3,
    stride=1,
    padding=1
)
output = conv.forward(images)
```

#### Activations
```moonlight
from ai.nn import ReLU, Softmax

relu = ReLU()
softmax = Softmax(dim=1)

x = relu.forward(x)
probs = softmax.forward(logits)
```

#### Sequential Model
```moonlight
from ai.nn import Sequential, Linear, ReLU

model = Sequential([
    Linear(784, 256, True),
    ReLU(),
    Linear(256, 128, True),
    ReLU(),
    Linear(128, 10, True)
])

output = model.forward(input)
```

### 3. ai.optim - Optimizers

#### SGD
```moonlight
from ai.optim import SGD

optimizer = SGD(
    model.parameters(),
    lr=0.01,
    momentum=0.9,
    weight_decay=0.0001
)

# Training loop
for (epoch = 0; epoch < num_epochs; epoch = epoch + 1) {
    loss = train_step(model, data)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
}
```

#### Adam
```moonlight
from ai.optim import Adam

optimizer = Adam(
    model.parameters(),
    lr=0.001,
    betas=[0.9, 0.999],
    eps=1e-8,
    weight_decay=0.0
)
```

### 4. ai.text - Text Generation & NLP

#### Load Models
```moonlight
from ai.text import load_model, generate_text

# Load GPT-2
model = load_model("gpt2", device="cuda")

# Generate text
text = generate_text(
    model,
    prompt="Once upon a time",
    max_length=100,
    temperature=0.8,
    top_k=50,
    top_p=0.95
)
```

#### Sentiment Analysis
```moonlight
from ai.text import sentiment_analysis

result = sentiment_analysis("I love this!", model)
print(result["label"])   # "positive"
print(result["score"])   # 0.95
```

#### Other Features
```moonlight
from ai.text import summarize, translate, question_answering

# Summarization
summary = summarize(long_text, model, max_length=50)

# Translation
translated = translate(text, "en", "pt", model)

# QA
answer = question_answering(context, question, model)
```

## Exemplos Completos

### Simple Neural Network
```moonlight
from ai.tensor import ones, zeros
from ai.nn import Sequential, Linear, ReLU
from ai.optim import SGD

# Build model
model = Sequential([
    Linear(10, 20, True),
    ReLU(),
    Linear(20, 2, True)
])

# Optimizer
optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=0.0001)

# Training
for (epoch = 0; epoch < 100; epoch = epoch + 1) {
    # Forward
    x = ones([32, 10], False)
    y_pred = model.forward(x)
    
    # Loss
    loss = compute_loss(y_pred, y_true)
    
    # Backward
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
}
```

### CNN for Images
```moonlight
from ai.nn import Conv2D, BatchNorm2d, Dropout, ReLU
from ai.optim import Adam

model = Sequential([
    Conv2D(3, 32, 3, 1, 1),
    BatchNorm2d(32),
    ReLU(),
    Dropout(0.25),
    
    Conv2D(32, 64, 3, 1, 1),
    BatchNorm2d(64),
    ReLU(),
    Dropout(0.25),
    
    Linear(64 * 8 * 8, 10, True)
])

optimizer = Adam(model.parameters(), lr=0.001, betas=[0.9, 0.999], eps=1e-8, weight_decay=0.0001)
```

### Text Generation
```moonlight
from ai.text import load_model, generate_text

model = load_model("gpt2", "cuda")

prompt = "The future of AI is"
text = generate_text(model, prompt, max_length=100, temperature=0.7, top_k=50, top_p=0.9)

print(text)
```

## Performance Tips

### 1. Use GPU
```moonlight
# Move model to GPU
for (param in model.parameters()) {
    param = param.cuda()
}

# Move data to GPU
x = x.cuda()
y = y.cuda()
```

### 2. Batch Processing
```moonlight
# Process in batches for efficiency
batch_size = 32
for (i = 0; i < len(data); i = i + batch_size) {
    batch = data[i:i+batch_size]
    output = model.forward(batch)
}
```

### 3. Mixed Precision (se disponível)
```moonlight
# Usar float16 para treinar mais rápido
# Requer suporte de hardware
```

## Bindings Python

A biblioteca AI usa bindings para:
- **PyTorch**: Backend principal para tensors e NN
- **Transformers** (HuggingFace): Modelos pré-treinados
- **TensorFlow**: Alternativa ao PyTorch

## Limitações Atuais

1. **Bindings**: Placeholders - requer integração real com PyTorch/TF
2. **Autograd**: Backprop simplificada
3. **Data Loading**: Sem DataLoader ainda
4. **Distributed**: Sem training distribuído
5. **Quantization**: Não implementada

## Roadmap AI Library

- [x] API de alto nível definida
- [x] Layers principais (Linear, Conv2D, ReLU)
- [x] Optimizers (SGD, Adam)
- [x] Text generation API
- [ ] Bindings PyTorch reais
- [ ] DataLoader e datasets
- [ ] Autograd completo
- [ ] Distributed training
- [ ] Model zoo

## Exemplos

Ver `examples/ai/`:
- `simple_nn.gpu` - Rede neural básica
- `cnn_image.gpu` - CNN para imagens
- `text_generation.gpu` - Geração de texto

## Referências

- [PyTorch Documentation](https://pytorch.org/docs/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [TensorFlow Documentation](https://www.tensorflow.org/)









