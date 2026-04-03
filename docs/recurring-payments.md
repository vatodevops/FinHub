# Pagos recurrentes y calendario financiero

## Objetivo

FinHub debe mostrar un calendario con pagos previsibles y aprender automáticamente cuándo un cargo parece recurrente.

Ejemplo:
- Internet cobrado el día 3 de cada mes
- suscripciones mensuales
- alquiler
- seguros trimestrales o anuales

## Qué debe hacer el sistema

### 1. Detectar recurrencia automáticamente
A partir del histórico de transacciones, detectar series como:
- mismo merchant o merchant parecido
- importe igual o cercano
- periodicidad estable
- canal compatible (`direct_debit`, `card`, etc.)

### 2. Crear una "serie recurrente"
Cada patrón recurrente detectado se guarda como una entidad separada.

Campos base:
- nombre sugerido
- merchant normalizado
- tipo (`monthly`, `weekly`, `quarterly`, `yearly`, `irregular`)
- intervalo estimado en días
- día habitual del mes
- importe medio
- desviación del importe
- próxima fecha estimada
- confianza
- auto_detected/manual_confirmed/manual_ignored

### 3. Mostrar calendario
Vista calendario / agenda con:
- próximos cargos estimados
- pagos confirmados manualmente
- importes esperados
- cuenta probable de cargo
- estado (`esperado`, `vencido`, `cobrado`, `omitido`)

### 4. Aprender con el tiempo
Si un patrón se confirma varias veces:
- aumenta confianza
- ajusta fecha estimada
- ajusta importe esperado

Si deja de aparecer:
- baja confianza
- se marca como inactivo tras cierto umbral

## Regla heurística inicial

Una serie recurrente candidata se detecta si hay al menos 3 movimientos con:
- merchant parecido
- periodicidad consistente
- diferencia temporal compatible
- importe dentro de una desviación razonable

### Periodicidades iniciales a soportar
- semanal: ~7 días
- mensual: 28-31 días
- bimestral: 59-62 días
- trimestral: 89-93 días
- anual: 364-366 días

## Casos típicos

### Recibo mensual fijo
- `MOVISTAR`
- 3 de cada mes
- 52.30 €

### Suscripción variable pequeña
- `SPOTIFY`
- alrededor del día 14
- 10.99 €

### Seguro anual
- `MAPFRE`
- una vez al año
- 410 €

## Casos problemáticos
- merchants con nombre inconsistente
- importes variables por consumo
- devoluciones
- cargos dobles puntuales
- cambios de fecha por festivos/fines de semana

## UX recomendada

No decidir todo en automático y a ciegas. Mejor:
- sugerir recurrencias detectadas
- permitir confirmar / editar / ignorar
- mostrar confianza

## MVP

### Backend
- tabla `recurring_series`
- tabla `recurring_occurrences`
- servicio de detección heurística
- endpoint de próximos pagos

### Frontend
- lista de pagos esperados próximos 30 días
- calendario mensual
- panel de sugerencias recurrentes detectadas

## Regla de negocio útil

Si un recibo mensual aparece 3 meses seguidos cerca del mismo día:
- se marca como recurrente candidato
- se estima el siguiente cobro para el mes siguiente

Si además coincide merchant + cuenta + rango de importe:
- confianza alta
