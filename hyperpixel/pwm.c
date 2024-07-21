/*
 * pwm.c
 *
 *  Created on: May 23 2018
 *  Author: Codedubix.eu
 */


#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

#include <pigpio.h>


#define NUM_GPIO 32
#define GPIO_INUSE 21
#define MIN_WIDTH 1000
#define MAX_WIDTH 2000


int main(int argc, char *argv[])
{
   unsigned int user_gpio, freq, real_freq = 0, duty_cycle = 0;


   if (gpioCfgClock(5, 1, 0)) return -1;

   if (gpioInitialise() < 0) return -1;


   if (argc != 4)
   {
      perror("Bad arguments : (1) GpioNumber, (2) Freq, (3) DutyCycle \n");
      perror("PWMfreq: 0 (off) or 1-125000000 (125M)\n");
      perror("PWMduty: 0 (off) to 1000000 (1M)(fully on)\n");
      return -1;
   }
   else
   {
      user_gpio = atoi(argv[1]);

      // if ((user_gpio>=0) && (user_gpio<NUM_GPIO)) used[user_gpio] = 1;
      // else return -1;
      if (!((user_gpio>=0) && (user_gpio<NUM_GPIO)))
         return -1;

      freq = atoi(argv[2]);
      duty_cycle = atoi(argv[3]);

   }


   int ret = gpioHardwarePWM(user_gpio, freq, duty_cycle);
   if (  ret != 0)
   {
      perror("PWM failed \n");
      return -1;
   }


   if( freq > 0 )
   {
      printf("Sending PWM to GPIO %d, Freq = %d, Duty Cycle = %d \n", user_gpio, freq, duty_cycle);
   }
   else
   {
      perror ("Bad pwm frequency \n");
   }


   return 0;

}
