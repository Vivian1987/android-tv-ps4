package org.androidtvps4.connectivity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
public final class StartReceiver extends BroadcastReceiver {
 @Override public void onReceive(Context context,Intent intent){
  ((ConnectivityKeeper)context.getApplicationContext()).ensureRequested();
 }
}
