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

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>

#include <pcan.h>
#include <libpcan.h>

/* #define VERB */

static void * canHandle;

static int dev_cnt = 0;      /* CAN devices counter */

void sendMsg(WORD ID, BYTE DATA[], int len)
{
  /* Procedure to send a CAN message */

  TPCANMsg Tmsg;

  Tmsg.ID = ID;
  Tmsg.MSGTYPE = MSGTYPE_STANDARD;
  Tmsg.LEN = len;
  int i, errno;

  for(i=0;i<len;i++) Tmsg.DATA[i] = DATA[i];
#ifdef VERB
    printf("--> 0x%03x  %d   ",Tmsg.ID,Tmsg.LEN);
    for(i=0;i<Tmsg.LEN;i++) printf("0x%02x  ",Tmsg.DATA[i]);
    printf("\n");    
#endif

    errno = CAN_Write(canHandle,&Tmsg);
}

int rcvMsgCob(int cob, BYTE DATA[], int timeout)
{
  TPCANRdMsg m;
  int errno;

#ifdef VERB
  int i;
#endif

  do{
    errno = LINUX_CAN_Read_Timeout(canHandle, &m, timeout);
  }while(m.Msg.ID != cob);

  if(errno==0){
#ifdef VERB
    printf("<-- 0x%03x  %d   ",m.Msg.ID,m.Msg.LEN);
    for(i=0;i<m.Msg.LEN;i++) printf("0x%02x  ",m.Msg.DATA[i]);
    printf("\n");    
#endif

    if(m.Msg.LEN != 0) memcpy(DATA,m.Msg.DATA,m.Msg.LEN);
    if(m.Msg.MSGTYPE & MSGTYPE_STATUS) CAN_Status(canHandle);
    return m.Msg.LEN;
  }
  else return 0;
}
  

int rcvMsg(BYTE DATA[], int timeout)
{
  TPCANRdMsg m;
  int errno;

#ifdef VERB
  int i;
#endif

  errno = LINUX_CAN_Read_Timeout(canHandle, &m, timeout);

  if(errno==0){
#ifdef VERB
    printf("<-- 0x%03x  %d   ",m.Msg.ID,m.Msg.LEN);
    for(i=0;i<m.Msg.LEN;i++) printf("0x%02x  ",m.Msg.DATA[i]);
    printf("\n");    
#endif

    if(m.Msg.LEN != 0) memcpy(DATA,m.Msg.DATA,m.Msg.LEN);
    if(m.Msg.MSGTYPE & MSGTYPE_STATUS) CAN_Status(canHandle);
    return m.Msg.LEN;
  }
  else return 0;
}

int canOpen()
{
  int bd;
  /* CAN initialization */

  char txt[VERSIONSTRING_LEN];

  if(!dev_cnt){  /* This task is performed only one time */
    bd = CAN_BAUD_500K;
    canHandle = LINUX_CAN_Open("/dev/pcan32",O_RDWR);

    if(!canHandle) return -1;
    CAN_VersionInfo(canHandle,txt);
    CAN_Init(canHandle, bd, CAN_INIT_TYPE_ST);
  }
  dev_cnt++;
  return 0;
}

void canClose()
{
  if(--dev_cnt == 0) {
    CAN_Close(canHandle);
  }
}

void canopen_synch()
{
  sendMsg(0x80,NULL,0);
}



