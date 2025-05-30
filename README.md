# Extração Multimodal de Vídeo do YouTube

Este projeto implementa uma solução para extrair e estruturar informações multimodais de vídeos do YouTube, incluindo metadados, transcrição de áudio e análise visual.

## Tecnologias Utilizadas

- **PytubeFix**: Para extração de vídeos do YouTube (fork atualizado do Pytube)
- **Whisper**: Modelo de transcrição de áudio (versão tiny para demonstração)
- **Gemini 2.0**: Modelo multimodal para análise de vídeo
- **UV**: Package manager rápido e eficiente
- **PyTorch**: Framework para processamento de vídeo

## Configuração

1. Clone o repositório

2. Primeiro, instale o `uv` (o instalador e resolvedor de pacotes Python):
   ```bash
   # No Windows.
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # No macOS e Linux.
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Instale as dependências:
   ```bash
   uv sync
   ```

4. Instale o PyTorch com suporte CUDA:
   ```bash
   uv run pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

5. Crie um arquivo `.env` baseado no `.env-example`:
   ```
   GOOGLE_API_KEY=
   MODEL=gemini-2.0-flash-001
   TEMPERATURE=0.0
   SPEECH_MODEL=openai/whisper-tiny
   ```

## Executando o Projeto

1. Execute os testes unitários:
   ```bash
   uv run pytest tests/ -v
   ```

2. Inicie o servidor:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Teste usando um vídeo do Youtube com o comando abaixo:
```bash
curl -X 'POST' 'http://localhost:8000/api/youtube/analyze/?youtube_url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DJzLtDZL7Nak'
```

## Notas

- O projeto utiliza o PytubeFix como alternativa ao Pytube devido a problemas de compatibilidade
- Whisper tiny foi escolhido para demonstração, mas pode ser substituído por versões mais robustas
- Gemini 2.0 foi selecionado por suas capacidades multimodais na análise de vídeo

## Melhorias futuras: 

- Processamento Paralelo
- Usar o estado da arte para análise de video **OpenVLM Leaderboard**: [Ver Rankings](https://huggingface.co/spaces/opencompass/open_vlm_leaderboard)
- Usar um modelo de transcrição melhor
