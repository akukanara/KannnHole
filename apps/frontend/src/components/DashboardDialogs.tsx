import { useState } from 'react';
import { Button, Dialog, Text, TextField, Theme } from '@radix-ui/themes';

export default function DashboardDialogs() {
  const [clientId, setClientId] = useState('');

  return (
    <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
      <div className="flex flex-wrap items-center gap-2">
        <Dialog.Root>
          <Dialog.Trigger>
            <Button className="h-8 rounded-lg bg-lime-500 px-3 text-xs font-semibold text-white transition-all duration-200 ease-in-out hover:bg-lime-600">
              Add New
            </Button>
          </Dialog.Trigger>
          <Dialog.Content
            maxWidth="460px"
            className="rounded-2xl border border-slate-200 bg-white/95 p-0 shadow-[0_20px_40px_rgba(2,6,23,0.22)] backdrop-blur-sm transition-all duration-200 ease-in-out data-[state=open]:animate-[contentShow_200ms_ease] dark:border-slate-800 dark:bg-slate-950/95"
          >
            <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
              <Dialog.Title className="text-base font-semibold tracking-tight text-slate-900 dark:text-slate-100">
                Create Client
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Simpan identitas client baru tanpa meninggalkan halaman dashboard.
              </Dialog.Description>
            </div>
            <div className="space-y-3 px-5 py-4">
              <label className="block space-y-1.5">
                <Text as="span" className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500 dark:text-slate-400">
                  Client ID
                </Text>
                <TextField.Root
                  value={clientId}
                  onChange={(event) => setClientId(event.target.value)}
                  placeholder="edge-sg-01"
                  className="h-9 rounded-lg border border-slate-200 bg-white text-sm transition-all duration-200 ease-in-out focus-within:border-lime-400 dark:border-slate-700 dark:bg-slate-900"
                />
              </label>
            </div>
            <div className="flex items-center justify-end gap-2 border-t border-slate-200 px-5 py-3 dark:border-slate-800">
              <Dialog.Close>
                <Button variant="soft" color="gray" className="h-8 rounded-lg px-3 text-xs transition-all duration-200 ease-in-out">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button
                disabled={!clientId.trim()}
                className="h-8 rounded-lg bg-lime-500 px-3 text-xs font-semibold text-white transition-all duration-200 ease-in-out hover:bg-lime-600 data-[disabled]:cursor-not-allowed data-[disabled]:opacity-45"
              >
                Save
              </Button>
            </div>
          </Dialog.Content>
        </Dialog.Root>

        <Dialog.Root>
          <Dialog.Trigger>
            <Button
              variant="soft"
              color="gray"
              className="h-8 rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 transition-all duration-200 ease-in-out hover:border-red-300 hover:text-red-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-red-500 dark:hover:text-red-300"
            >
              Delete Confirmation
            </Button>
          </Dialog.Trigger>
          <Dialog.Content
            maxWidth="420px"
            className="rounded-2xl border border-slate-200 bg-white/95 p-0 shadow-[0_20px_40px_rgba(2,6,23,0.22)] backdrop-blur-sm transition-all duration-200 ease-in-out dark:border-slate-800 dark:bg-slate-950/95"
          >
            <div className="px-5 py-4">
              <Dialog.Title className="text-base font-semibold text-slate-900 dark:text-slate-100">
                Delete Tunnel Profile?
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Aksi ini tidak dapat dibatalkan. Pastikan data sudah dibackup.
              </Dialog.Description>
            </div>
            <div className="flex items-center justify-end gap-2 border-t border-slate-200 px-5 py-3 dark:border-slate-800">
              <Dialog.Close>
                <Button variant="soft" color="gray" className="h-8 rounded-lg px-3 text-xs">
                  Keep Data
                </Button>
              </Dialog.Close>
              <Dialog.Close>
                <Button color="red" className="h-8 rounded-lg px-3 text-xs font-semibold">
                  Delete
                </Button>
              </Dialog.Close>
            </div>
          </Dialog.Content>
        </Dialog.Root>
      </div>
    </Theme>
  );
}
