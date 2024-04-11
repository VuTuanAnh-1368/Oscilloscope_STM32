#include "stm32f10x.h"

#define GPIOA_CRL    (*((volatile uint32_t*)0x40010800))
#define GPIOA_CRH    (*((volatile uint32_t*)0x40010804))
#define ADC1_SR      (*((volatile uint32_t*)0x40012400))
#define ADC1_CR1     (*((volatile uint32_t*)0x40012404))
#define ADC1_CR2     (*((volatile uint32_t*)0x40012408))
#define ADC1_SMPR2   (*((volatile uint32_t*)0x40012410))
#define ADC1_SQR3    (*((volatile uint32_t*)0x40012434))
#define ADC1_DR      (*((volatile uint32_t*)0x4001244C))
#define USART1_SR    (*((volatile uint32_t*)0x40013800))
#define USART1_DR    (*((volatile uint32_t*)0x40013804))
#define USART1_BRR   (*((volatile uint32_t*)0x40013808))
#define USART1_CR1   (*((volatile uint32_t*)0x4001380C))
#define RCC_APB2ENR     *(volatile unsigned int *)(RCC_BASE + 0x18)
#define RCC_CFGR        *(volatile unsigned int *)(RCC_BASE + 0x04)
#define ADC1_EOC (1 << 1)

void Clock_Config(void) ;
void GPIO_Config(void);
void ADC_Config(void);
void USART1_Config(void);
void Transmit_UART(uint32_t data) ;

int main(void) {
		Clock_Config() ;
		GPIO_Config();
		ADC_Config();
		USART1_Config();
    while (1) {
        ADC1->CR2 |= ADC_CR2_ADON;  
        while (!(ADC1->SR & ADC_SR_EOC)); 
        uint32_t adcValue = ADC1->DR; 
        Transmit_UART(adcValue); 
			  for (volatile int i = 0; i < 1000; i++);
			}
}
void Clock_Config(void) {
    RCC_APB2ENR |= (1 << 2) | (1 << 9) | (1 << 14);
	  RCC_CFGR |= (1 << 14);
}
void GPIO_Config(void) {
    GPIOA_CRH &= ~(0xF << (4 * (9 - 8))); 
	  GPIOA_CRH |= (0xB << (4 * (9 - 8)));
}
void ADC_Config(void) {
    ADC1_CR2 |= (1 << 0); 
    ADC1_CR2 |= (1 << 2); 
    while (ADC1_CR2 & (1 << 2)); 
    ADC1_SMPR2 |= (7 << 0); 
    ADC1_SQR3 = 0; 
}
void USART1_Config(void) {
    USART1_BRR = 0x341;
    USART1_CR1 |= (1 << 13) | (1 << 3) | (1 << 2);
}
void Transmit_UART(uint32_t data) {
    while (!(USART1->SR & USART_SR_TXE));
    USART1->DR = (data >> 4) & 0xFF; 
    while (!(USART1->SR & USART_SR_TC));

    while (!(USART1->SR & USART_SR_TXE));
    USART1->DR = data & 0x0F; 
    while (!(USART1->SR & USART_SR_TC));
}