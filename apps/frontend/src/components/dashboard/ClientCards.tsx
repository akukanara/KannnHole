import { useState, useEffect } from 'react';
import { Card, Text, Badge, Button, Dialog, TextField, Grid, Flex, Box, Theme } from '@radix-ui/themes';
import { IconCopy, IconTerminal2, IconExternalLink, IconTrash } from '@tabler/icons-react';

interface Client {
  client_id: string;
  token: string;
  owner: string | null;
  tunnels: number;
  installer: string;
}

export default function ClientCards() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/clients')
      .then((res) => res.json())
      .then((data) => {
        setClients(data.clients || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Optional: add a toast notification here
  };

  if (loading) {
    return (
      <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
        <Text>Loading clients...</Text>
      </Theme>
    );
  }

  if (clients.length === 0) {
    return (
      <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
        <Card size="3" className="text-center py-12 border-dashed">
          <Text color="gray">No clients found. Create one above to get started.</Text>
        </Card>
      </Theme>
    );
  }

  return (
    <Theme accentColor="lime" grayColor="sand" radius="large" scaling="100%">
      <Grid columns={{ initial: '1', sm: '2', lg: '3' }} gap="4">
        {clients.map((client) => (
          <Card key={client.client_id} size="2" className="flex flex-col justify-between hover:shadow-md transition-shadow">
            <Box mb="3">
              <Flex justify="between" align="center" mb="1">
                <Text weight="bold" size="4">{client.client_id}</Text>
                <Badge color="lime" variant="soft">
                  {client.tunnels} Tunnels
                </Badge>
              </Flex>
              <Text size="2" color="gray" mb="2" className="block">Owner: {client.owner || 'Unknown'}</Text>
            </Box>

            <Flex gap="2" mt="auto">
              <Dialog.Root>
                <Dialog.Trigger>
                  <Button variant="surface" size="2" className="flex-1">
                    <IconTerminal2 size={16} className="mr-1" /> Installer
                  </Button>
                </Dialog.Trigger>
                <Dialog.Content maxWidth="550px">
                  <Dialog.Title>Installer Script</Dialog.Title>
                  <Dialog.Description size="2" mb="4">
                    Run this command on your remote machine to install and connect this client.
                  </Dialog.Description>
                  
                  <Box className="bg-slate-950 p-4 rounded-lg relative group mb-4">
                    <code className="text-lime-400 text-xs break-all block pr-8">
                      {client.installer}
                    </code>
                    <Button 
                      variant="ghost" 
                      color="gray" 
                      size="1" 
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => copyToClipboard(client.installer)}
                    >
                      <IconCopy size={14} />
                    </Button>
                  </Box>

                  <Flex gap="3" mt="4" justify="end">
                    <Dialog.Close>
                      <Button variant="soft" color="gray">Close</Button>
                    </Dialog.Close>
                  </Flex>
                </Dialog.Content>
              </Dialog.Root>

              <a href={`/clients/${client.client_id}/tunnels`} className="flex-1">
                <Button variant="soft" color="lime" size="2" className="w-full">
                  <IconExternalLink size={16} className="mr-1" /> Manage
                </Button>
              </a>
            </Flex>
          </Card>
        ))}
      </Grid>
    </Theme>
  );
}
