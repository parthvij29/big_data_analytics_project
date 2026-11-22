create table if not exists public.contact_messages (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  email text not null check (length(email) <= 254 and email like '%_@_%._%'),
  message text not null check (length(trim(message)) between 3 and 3000)
);
alter table public.contact_messages enable row level security;
revoke all on public.contact_messages from public, anon, authenticated;
grant insert (email, message) on public.contact_messages to anon;
drop policy if exists "Submit contact message" on public.contact_messages;
create policy "Submit contact message" on public.contact_messages for insert to anon with check (true);
