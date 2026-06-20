// Supabase Client for Node.js / Frontend JavaScript applications
// Install dependency: npm install @supabase/supabase-js

const { createClient } = require('@supabase/supabase-js');

// These should be configured in your Node.js application environment variables (.env)
const supabaseUrl = process.env.SUPABASE_URL || 'https://your-project-id.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY || 'your-supabase-anon-key';

if (!supabaseUrl || !supabaseKey) {
  console.warn('Warning: SUPABASE_URL or SUPABASE_KEY environment variables are missing.');
}

const supabase = createClient(supabaseUrl, supabaseKey);

module.exports = { supabase };
