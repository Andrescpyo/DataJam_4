# Resumen del análisis espacial de Bogotá D.C. (2023-2024)

## Resultado principal

Se construyó una tabla final con 66 observaciones: 33 UPL para 2023 y 33 UPL para 2024. La unidad espacial base es la UPL y la estructura final incluye temperatura media, PM2.5, población y densidad de arbolado como variable disponible cuando el raster puede leerse.

## Evidencia validada

- Número de registros: 66
- Número de UPL: 33
- Años: 2023 y 2024
- Archivo generado: data/processed/df_final.csv

## Estadísticas descriptivas

### Temperatura media superficial
- 2023: 15.258 °C
- 2024: 15.584 °C

### PM2.5 promedio anual
- 2023: 15.078 µg/m³
- 2024: 16.658 µg/m³

### Población por UPL (promedio por año)
- 2023: 265,450.208
- 2024: 265,792.833

## Correlaciones observadas

Con la tabla final y considerando el total de UPL por año:
- Temperatura y PM2.5: r = 0.603
- Temperatura y población: r = -0.091
- PM2.5 y población: r = 0.171

Esto indica una asociación positiva moderada entre calor y contaminación, pero no evidencia causal.

## UPL con mayor exposición térmica

1. UPL18 (2024): 16.210 °C, PM2.5 21.739
2. UPL31 (2024): 16.008 °C, PM2.5 16.566
3. UPL18 (2023): 16.002 °C, PM2.5 18.309
4. UPL19 (2024): 15.921 °C, PM2.5 19.491
5. UPL24 (2024): 15.871 °C, PM2.5 14.995

## UPL con mayor PM2.5

1. UPL18 (2024): 21.739
2. UPL14 (2023): 20.655
3. UPL16 (2023): 19.793
4. UPL17 (2024): 19.565
5. UPL19 (2024): 19.491

## Limitación metodológica importante

La variable de densidad de arbolado no fue computable en este entorno porque el raster oficial del Jardín Botánico no se abrió con la exportación disponible en la sesión. Por esta razón, la columna de densidad se registró como NA y se documentó explícitamente. Esto no invalida el resto del flujo, pero sí limita la comparación con vegetación urbana en esta ejecución exacta.

## Conclusión

La base analítica reproducible quedó construida sobre UPL, población, temperatura y PM2.5 para 2023 y 2024. Los resultados muestran un patrón espacial consistente de mayor calor asociado a mayor contaminación, pero la lectura debe mantenerse descriptiva y espacial, sin atribuir causalidad.
