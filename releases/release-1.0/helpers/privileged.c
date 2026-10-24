#include "jailbreak.h"
int ps4_as_root(void (*fn)(void *),void *argument){
 struct jbc_cred old,root;
 if(jbc_get_cred(&old))return -1;
 root=old;
 if(jbc_jailbreak_cred(&root))return -1;
 if(jbc_set_cred(&root))return -1;
 fn(argument);
 return jbc_set_cred(&old);
}
