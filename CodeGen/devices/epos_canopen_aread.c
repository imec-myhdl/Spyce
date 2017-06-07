/*
COPYRIGHT (C) 2016  Roberto Bucher (roberto.bucher@supsi.ch)

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
*/

#include <pyblock.h>
#include <stdio.h>

#define BYTE unsigned char
#define WORD unsigned short
#define DWORD unsigned int

#define TIMEOUT -1

#include <canopen.h>
#include <stdlib.h>
#include <unistd.h>

static BYTE NMT_pre[2]  = {0x80, 0x00};
static BYTE NMT_act[2]  = {0x01, 0x00};

static BYTE unsetPDO[8][8] = {
  {0x22, 0x00, 0x16, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x01, 0x16, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x02, 0x16, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x03, 0x16, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x00, 0x1A, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x01, 0x1A, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x02, 0x1A, 0x00, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x03, 0x1A, 0x00, 0x00, 0x00, 0x00, 0x00},
};

#define DATA_SIZE 4

static BYTE data[DATA_SIZE][8]= {
  {0x22, 0x40, 0x60, 0x00, 0x80, 0x00, 0x00, 0x00},
  {0x22, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00},
  {0x22, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00},
  {0x22, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00},
};

static BYTE reset[8]    = {0x22, 0x03, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00};
static BYTE read_req[8] = {0x40, 0x7C, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00};
static BYTE mode_req[8] = {0x40, 0x61, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00};
static BYTE set_mode[8] = {0x22, 0x60, 0x60, 0x00, 0xFD, 0x00, 0x00, 0x00};

static void init(python_block *block)
{
  int i;
  BYTE DATA[8];

  if(canOpen()) exit(1);

  NMT_pre[1] = (BYTE) block->intPar[0];
  NMT_act[1] = (BYTE) block->intPar[0];

  sendMsg(0x000,NMT_pre,2);

  for(i=0;i<8;i++){
    sendMsg(0x600+block->intPar[0],unsetPDO[i],8);  /* configure device */
    rcvMsg(DATA, TIMEOUT);
    usleep(50000);
  }
  sendMsg(0x000,NMT_act,2);   /* Operationa status */

  sendMsg(0x600+block->intPar[0],reset,8);

  do{
    rcvMsg(DATA, TIMEOUT);
    usleep(100000);
  }while(DATA[0]!=0x60);

  read_req[3] = block->intPar[1]+1;

  for(i=0;i<DATA_SIZE;i++){
    sendMsg(0x600+block->intPar[0],data[i],8); /* Configure CAN device */
    rcvMsg(DATA, TIMEOUT);
    usleep(100000);
  }

  sendMsg(0x600+block->intPar[0],mode_req,8);
  rcvMsg(DATA, TIMEOUT);
  usleep(100000);
  if(DATA[4]==0x01) {
    sendMsg(0x600+block->intPar[0],set_mode,8);
    rcvMsg(DATA, TIMEOUT);
    usleep(100000);
  }
}

static void inout(python_block *block)
{
  BYTE DATA[8];
  short int * counter;
  int len;
  double *y = block->y[0];
  unsigned short *index;

  sendMsg(0x600+block->intPar[0],read_req,8);
  do{
    len = rcvMsg(DATA, TIMEOUT);
    index = (unsigned short *) &DATA[1];
  }while(*index != 0x207C);

  if(len>0){
    counter = (short int *) &(DATA[4]);
    y[0] = 0.001*(*counter);
  }
}

static void end(python_block *block)
{
  canClose();
}

void epos_canopen_aread(int Flag, python_block *block)
{
  if (Flag==OUT){          /* set output */
    inout(block);
  }
  else if (Flag==END){     /* termination */ 
    end(block);
  }
  else if (Flag==INIT){    /* initialisation */
    init(block);
  }
}


