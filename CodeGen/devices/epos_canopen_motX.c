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

#define DATA_SIZE 10

static BYTE data[DATA_SIZE][8]= {
  {0x22, 0x40, 0x60, 0x00, 0x80, 0x00, 0x00, 0x00},
  {0x22, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00},
  {0x22, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00},
  {0x22, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00},
  {0x22, 0xFB, 0x60, 0x01, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0xFB, 0x60, 0x02, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0xFB, 0x60, 0x03, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0xFB, 0x60, 0x04, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0xFB, 0x60, 0x05, 0x00, 0x00, 0x00, 0x00},
  {0x22, 0x60, 0x60, 0x00, 0xFF, 0x00, 0x00, 0x00},
};

static BYTE reset[8]={0x22, 0x03, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00};
static BYTE write_req[8]={0x22,0x62,0x20,0x00,0x00,0x00,0x00,0x00};

static void init(python_block *block)
{
  int i;
  BYTE DATA[8];
  short int * val;

  if(canOpen()) exit(1);

  NMT_pre[1] = (BYTE) block->intPar[0];
  NMT_act[1] = (BYTE) block->intPar[0];

  val = (short int *) &(data[4][4]);
  *val = (short int) (block->realPar[0]);
  val = (short int *) &(data[5][4]);
  *val = (short int) (block->realPar[1]);
  val = (short int *) &(data[6][4]);
  *val = (short int) (block->realPar[2]);
  val = (short int *) &(data[7][4]);
  *val = (short int) (block->realPar[4]);
  val = (short int *) &(data[8][4]);
  *val = (short int) (block->realPar[5]);

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
    usleep(50000);
  }while(DATA[0]!=0x60);

  for(i=0;i<DATA_SIZE;i++){
    sendMsg(0x600+block->intPar[0],data[i],8);  /* configure device */
    rcvMsg(DATA, TIMEOUT);
    usleep(50000);
  }
}

static void inout(python_block *block)
{
  int *U_can;

  BYTE DATA[8];
  double *u = block->u[0];
  unsigned short *index;

  U_can = (int *) &write_req[4];
  *U_can = (int) u[0];

  sendMsg(0x600+block->intPar[0],write_req,8);
  do{
    rcvMsg(DATA, TIMEOUT);
    index =  (unsigned short*) &DATA[1];
  }while(*index != 0x2062);
}

static void end(python_block *block)
{
  int *U_can;
  BYTE DATA[8];
  unsigned short *index;

  U_can = (int *) &write_req[4];
  *U_can = 0;

  sendMsg(0x600+block->intPar[0],write_req,8);
  do{
    rcvMsg(DATA, TIMEOUT);
    index = (unsigned short*) &DATA[1];
  }while(*index != 0x2062);
   
  canClose();
}

void epos_canopen_motX(int Flag, python_block *block)
{
  if (Flag==OUT){          /* set output */
    inout(block);
  }
  else if (Flag==END){     /* termination */ 
    end(block);
  }
  else if (Flag ==INIT){    /* initialisation */
    init(block);
  }
}


