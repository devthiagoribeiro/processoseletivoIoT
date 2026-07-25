import machine
import time

# Configuração de Pinos
ldr = machine.ADC(machine.Pin(34))
ldr.atten(machine.ADC.ATTN_11DB)
btn = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Variáveis de Estado
total_pecas = 0
peca_bloqueando = False
alerta_emitido = False
tempo_inicio_bloqueio = 0

# Constantes de Calibração do Wokwi
ADC_CLARO = 999   # Valor do ADC quando o LDR está sob luz do ambiente (ex: > 500 lux)
ADC_ESCURO = 2045 # Valor do ADC quando o LDR está coberto (ex: < 100 lux)

TEMPO_MICRO_PARADA = 5000 # 5 segundos

# Mensagem de inicialização
print("Contador de Producao Inicializado")

while True:
    # Leitura dos sensores
    adc_val = ldr.read()
    btn_val = btn.value()

    # Lógica de Reset do Turno
    if btn_val == 1:
        time.sleep_ms(50)
        if btn.value() == 1:
            total_pecas = 0
            peca_bloqueando = False
            alerta_emitido = False
            print("Turno resetado com sucesso. Contadores zerados.")
            # Debounce do botão: espera até que o botão seja liberado
            while btn.value() == 1:
                time.sleep_ms(20)
    
    # Avalia se a peça está na frente (bloqueando a luz)
    estado_atual_bloqueado = (adc_val > ADC_ESCURO)
    
    # Verifica se ainda não entrou na máquina de estados bloqueada
    if estado_atual_bloqueado and not peca_bloqueando:
        peca_bloqueando = True # Entra no estado do bloqueio
        tempo_inicio_bloqueio = time.ticks_ms()
        alerta_emitido = False
    
    # Verifica se na ultima leitura a peça estava na frente do sensor e transicionou para linha livre
    elif peca_bloqueando and (adc_val < ADC_CLARO):
        peca_bloqueando = False
        total_pecas += 1
        print(f"Peca detectada! Total: {total_pecas}")
        
    # Lógica de Micro-paradas (Cronômetro Não-Bloqueante)
    if peca_bloqueando and not alerta_emitido:
        tempo_passado = time.ticks_diff(time.ticks_ms(), tempo_inicio_bloqueio)
        if tempo_passado >= TEMPO_MICRO_PARADA:
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    time.sleep_ms(20)