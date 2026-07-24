import machine
import time

# 1. Configuração de Pinos
ldr = machine.ADC(machine.Pin(34))
ldr.atten(machine.ADC.ATTN_11DB) # Permite ler a faixa total de 0 a 3.3V (Valores de 0 a 4095)
btn = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# 2. Variáveis de Estado
total_pecas = 0
peca_bloqueando = False
alerta_emitido = False
tempo_inicio_bloqueio = 0

# 3. Constantes Base
# Com o divisor de tensão: Lux Alto (800) = ADC > 3000 / Lux Baixo (50) = ADC < 2000
LIMIAR_ADC = 2400 
TEMPO_MICRO_PARADA = 5000 # 5 segundos

# Inicialização exigida pelo CI
print("Contador de Producao Inicializado")

while True:
    # Leitura dos sensores
    adc_val = ldr.read()
    btn_val = btn.value()
    
    estado_atual_bloqueado = adc_val < LIMIAR_ADC
    
    # ---------------------------------------------------------
    # A. Lógica de Contagem (Transição de borda)
    # ---------------------------------------------------------
    if estado_atual_bloqueado and not peca_bloqueando:
        # A peça acabou de entrar na frente do sensor (Borda de descida da luz)
        peca_bloqueando = True
        tempo_inicio_bloqueio = time.ticks_ms()
        alerta_emitido = False
        
    elif not estado_atual_bloqueado and peca_bloqueando:
        # A peça saiu da frente do sensor (Borda de subida da luz) -> Incrementa
        peca_bloqueando = False
        total_pecas += 1
        print(f"Peca detectada! Total: {total_pecas}")
        
    # ---------------------------------------------------------
    # B. Lógica de Micro-paradas (Cronômetro Não-Bloqueante)
    # ---------------------------------------------------------
    if peca_bloqueando and not alerta_emitido:
        tempo_passado = time.ticks_diff(time.ticks_ms(), tempo_inicio_bloqueio)
        if tempo_passado >= TEMPO_MICRO_PARADA:
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    # ---------------------------------------------------------
    # C. Lógica de Reset de Turno
    # ---------------------------------------------------------
    if btn_val == 0:
        time.sleep_ms(50) # Debounce de segurança
        if btn.value() == 0:
            total_pecas = 0
            peca_bloqueando = False
            alerta_emitido = False
            print("Turno resetado com sucesso. Contadores zerados.")
            
            # Aguarda o botão ser solto para não flodar a serial
            while btn.value() == 0:
                time.sleep_ms(20)

    # Pequeno atraso no loop para não sobrecarregar o simulador (Wokwi)
    time.sleep_ms(20)