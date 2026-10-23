"""Port Android's GPL quota2 match to this kernel with namespace-local accounting."""
from pathlib import Path
import subprocess,shutil,difflib
project=Path(__file__).resolve().parent.parent
ref=project/'reference/android-kernel-netfilter'
root=Path('/home/amber/projects/ps4-android/quota2')
root.mkdir(exist_ok=True)
(root/'include/linux/netfilter').mkdir(parents=True,exist_ok=True)
a=(ref/'xt_quota2.c').read_text();s=a
s=s.replace('#include <net/netlink.h>','#include <net/netlink.h>\n#include <net/netns/generic.h>')
s=s.replace('struct xt_quota_counter {','struct xt_quota_counter {\n\tstruct net *net;')
s=s.replace('static struct sock *nflognl;','')
s=s.replace('static struct proc_dir_entry *proc_xt_quota;', '''/* Each Android network namespace owns its proc counters and alert socket. */
static unsigned int quota_net_id;
struct quota_net {
	struct proc_dir_entry *dir;
	struct sock *nflognl;
};''')
s=s.replace('static void quota2_log(unsigned int hooknum,','static void quota2_log(struct net *net, unsigned int hooknum,')
s=s.replace('netlink_broadcast(nflognl,','netlink_broadcast(((struct quota_net *)net_generic(net, quota_net_id))->nflognl,')
s=s.replace('strlcpy(', 'strscpy(')
s=s.replace('PDE_DATA(', 'pde_data(')
s=s.replace('q2_get_counter(const struct xt_quota_mtinfo2 *q)','q2_get_counter(const struct xt_quota_mtinfo2 *q, struct net *net)')
s=s.replace('if (strcmp(e->name, q->name) == 0)', 'if (e->net == net && strcmp(e->name, q->name) == 0)')
s=s.replace('\te = new_e;','\te = new_e;\n\te->net = net;')
s=s.replace('proc_xt_quota, &q2_counter_fops, e)', '((struct quota_net *)net_generic(net, quota_net_id))->dir, &q2_counter_fops, e)')
s=s.replace('q->master = q2_get_counter(q);','q->master = q2_get_counter(q, par->net);')
s=s.replace('remove_proc_entry(e->name, proc_xt_quota);', 'remove_proc_entry(e->name, ((struct quota_net *)net_generic(par->net, quota_net_id))->dir);')
s=s.replace('quota2_log(xt_hooknum(par),','quota2_log(xt_net(par), xt_hooknum(par),')
x=s.index('static int __init quota_mt2_init(void)');y=s.index('module_init(quota_mt2_init);',x)
s=s[:x]+'''static int __net_init quota_net_init(struct net *net)
{
	struct quota_net *qn = net_generic(net, quota_net_id);
	qn->dir = proc_mkdir("xt_quota", net->proc_net);
	if (!qn->dir)
		return -ENOMEM;
	qn->nflognl = netlink_kernel_create(net, NETLINK_NFLOG, NULL);
	if (!qn->nflognl) {
		remove_proc_entry("xt_quota", net->proc_net);
		return -ENOMEM;
	}
	return 0;
}

static void __net_exit quota_net_exit(struct net *net)
{
	struct quota_net *qn = net_generic(net, quota_net_id);
	netlink_kernel_release(qn->nflognl);
	remove_proc_entry("xt_quota", net->proc_net);
}

static struct pernet_operations quota_net_ops = {
	.init = quota_net_init,
	.exit = quota_net_exit,
	.id = &quota_net_id,
	.size = sizeof(struct quota_net),
};

static int __init quota_mt2_init(void)
{
	int ret = register_pernet_subsys(&quota_net_ops);
	if (ret)
		return ret;
	ret = xt_register_matches(quota_mt2_reg, ARRAY_SIZE(quota_mt2_reg));
	if (ret)
		unregister_pernet_subsys(&quota_net_ops);
	return ret;
}

static void __exit quota_mt2_exit(void)
{
	xt_unregister_matches(quota_mt2_reg, ARRAY_SIZE(quota_mt2_reg));
	unregister_pernet_subsys(&quota_net_ops);
}

'''+s[y:]
(root/'xt_quota2.c').write_text(s)
shutil.copyfile(ref/'xt_quota2.h',root/'include/linux/netfilter/xt_quota2.h')
(project/'patches/quota2-namespace-port.patch').write_text(''.join(difflib.unified_diff(a.splitlines(True),s.splitlines(True),fromfile='android13-5.15/xt_quota2.c',tofile='cole/xt_quota2.c')))
(root/'Makefile').write_text('obj-m += xt_quota2.o\nccflags-y += -I$(src)/include -DCONFIG_NETFILTER_XT_MATCH_QUOTA2_LOG\n')
subprocess.run(['make','-C','/home/amber/projects/ps4-android/kernel-6.15.4','modules_prepare'],check=True)
subprocess.run(['make','-C','/home/amber/projects/ps4-android/kernel-6.15.4','M='+str(root),'KBUILD_EXTRA_SYMBOLS=/home/amber/projects/ps4-android/kernel-6.15.4/vmlinux.symvers','-j4','modules'],check=True)
