package com.example.zylocation;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class StartZYLocationServiceAtBootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
		Log.d("ZYLOCATION", "StartZYLocationServiceAtBootReceiver.onReceive");
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            Intent serviceIntent = new Intent(context, ZYLocationService.class);
            context.startService(serviceIntent);
			Log.d("ZYLOCATION", "service started");
        }
    }
}