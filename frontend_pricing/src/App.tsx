import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ArrowRight, ChevronDown, ShieldCheck, Sparkles } from 'lucide-react';

interface DjangoPlan {
  id?: number;
  pk?: number;
  tier: string;
  name: string;
  price_monthly: number;
  reach_limit: number;
  whatsapp_enabled: boolean;
  facebook_enabled: boolean;
  description: string;
}

// Fallback plans if loaded outside Django
const FALLBACK_PLANS: DjangoPlan[] = [
  {
    pk: 1,
    tier: 'basic',
    name: 'Basic',
    price_monthly: 100,
    reach_limit: 1000,
    whatsapp_enabled: false,
    facebook_enabled: false,
    description: "Free plan. The platform will reach out to 5 potential customers in your city who need your type of service."
  },
  {
    pk: 2,
    tier: 'pro',
    name: 'Pro',
    price_monthly: 500,
    reach_limit: 5000,
    whatsapp_enabled: true,
    facebook_enabled: false,
    description: "The platform will reach out to 100 potential customers via WhatsApp in your city who need your type of service."
  },
  {
    pk: 3,
    tier: 'max',
    name: 'Max',
    price_monthly: 1500,
    reach_limit: 10000,
    whatsapp_enabled: true,
    facebook_enabled: true,
    description: "The platform will reach out to 10,000 potential customers via WhatsApp AND Facebook in your city who need your type of service."
  }
];

export default function App() {
  const [plans, setPlans] = useState<DjangoPlan[]>(FALLBACK_PLANS);
  const [isYearly, setIsYearly] = useState(false);
  const [userAuthenticated, setUserAuthenticated] = useState(false);
  const [registerUrl, setRegisterUrl] = useState('/accounts/register/');
  const [subscribeUrlTemplate, setSubscribeUrlTemplate] = useState('/subscriptions/subscribe/__PLAN_ID__/');

  // Read Django config attributes
  useEffect(() => {
    const rootEl = document.getElementById('pricing-root');
    if (rootEl) {
      const rawPlans = rootEl.getAttribute('data-plans-json');
      if (rawPlans) {
        try {
          const parsed = JSON.parse(rawPlans);
          if (parsed && parsed.length > 0) {
            setPlans(parsed);
          }
        } catch (e) {
          console.error("Failed to parse Django plans json", e);
        }
      }
      setUserAuthenticated(rootEl.getAttribute('data-user-authenticated') === 'true');
      setRegisterUrl(rootEl.getAttribute('data-register-url') || '/accounts/register/');
      setSubscribeUrlTemplate(rootEl.getAttribute('data-subscribe-url') || '/subscriptions/subscribe/__PLAN_ID__/');
    }
  }, []);

  const getBillingActionUrl = (planId: number) => {
    if (userAuthenticated) {
      return subscribeUrlTemplate.replace('__PLAN_ID__', String(planId));
    }
    return registerUrl;
  };

  // 20% discount on yearly billing
  const getDisplayPrice = (monthlyPrice: number) => {
    if (isYearly) {
      return Math.round(monthlyPrice * 0.8);
    }
    return monthlyPrice;
  };

  // FAQ Accordion State
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);

  const FAQS = [
    {
      q: "How does the customer matching work?",
      a: "Our platform continuously aggregates and cleans a localized directory of customers who opted in to receive service offers in their cities. When you subscribe, we automatically scan our database for matching leads based on your city and service category."
    },
    {
      q: "What channels are used for outreaches?",
      a: "Depending on your plan, we use official WhatsApp templates and automated Facebook Page messages. The Basic plan uses standard emails, the Pro plan introduces WhatsApp campaigns, and the Max plan operates across both WhatsApp and Facebook messaging."
    },
    {
      q: "Can I upgrade or downgrade my plan at any time?",
      a: "Yes. Upgrades take effect immediately and credit your remaining billing period. Downgrades take effect at the end of your current active billing cycle."
    },
    {
      q: "Are there any setup fees or hidden costs?",
      a: "No setup fees. You pay the flat monthly subscription rate shown above. Standard gateway transaction processing fees are covered within the price."
    }
  ];

  return (
    <div className="min-h-screen bg-[#030712] text-gray-150 py-16 px-4 sm:px-6 lg:px-8 relative selection:bg-indigo-500 selection:text-white">
      {/* Background Spotlight */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[350px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center mb-16 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-semibold uppercase tracking-wider mb-6"
        >
          <Sparkles size={12} /> Pricing Plans
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="font-heading text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6"
        >
          Scale Your Local <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">Reach</span>
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-gray-400 text-lg max-w-xl mx-auto leading-relaxed"
        >
          Clear, predictable plans designed to connect your local business with customers who need your talent.
        </motion.p>
      </div>

      {/* Billing Toggle */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="flex justify-center items-center gap-4 mb-16 relative z-10"
      >
        <span className={`text-sm font-semibold transition-colors ${!isYearly ? 'text-white' : 'text-gray-500'}`}>Monthly</span>
        <button
          onClick={() => setIsYearly(!isYearly)}
          className="w-12 h-7 rounded-full bg-gray-900 border border-white/10 p-0.5 transition-colors relative flex items-center"
        >
          <motion.div
            layout
            className="w-5 h-5 rounded-full bg-indigo-500 shadow-lg"
            animate={{ x: isYearly ? 20 : 0 }}
            transition={{ type: "spring", stiffness: 500, damping: 30 }}
          />
        </button>
        <span className={`text-sm font-semibold transition-colors flex items-center gap-1.5 ${isYearly ? 'text-white' : 'text-gray-500'}`}>
          Yearly
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
            Save 20%
          </span>
        </span>
      </motion.div>

      {/* Pricing Cards Grid */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch mb-24 relative z-10">
        <AnimatePresence>
          {plans.map((plan, idx) => {
            const planId = plan.id || plan.pk || 1;
            const isPro = plan.tier === 'pro';
            const isMax = plan.tier === 'max';
            
            return (
              <motion.div
                key={plan.tier}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * idx }}
                whileHover={{ y: -8, transition: { duration: 0.2 } }}
                className={`flex flex-col justify-between p-8 rounded-3xl border transition-all duration-300 relative bg-[#0b0f19]/80 backdrop-blur-xl ${
                  isPro 
                    ? 'border-2 border-indigo-500 shadow-[0_0_35px_rgba(99,102,241,0.15)] bg-gray-900/40 md:scale-105 z-10' 
                    : 'border-white/5 hover:border-white/10'
                }`}
              >
                {isPro && (
                  <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-1 bg-gradient-to-r from-indigo-500 to-purple-500 text-[9px] font-bold text-white uppercase tracking-widest rounded-full shadow-lg border border-indigo-400/20">
                    Most Popular
                  </span>
                )}

                <div>
                  <h3 className={`text-sm font-bold tracking-wider uppercase mb-2 ${
                    isPro ? 'text-indigo-400' : isMax ? 'text-amber-400' : 'text-gray-400'
                  }`}>
                    {plan.name}
                  </h3>
                  
                  <div className="font-heading text-4xl font-extrabold text-white my-4 flex items-baseline gap-1">
                    ₹{getDisplayPrice(plan.price_monthly)}
                    <span className="text-xs text-gray-500 font-normal">/mo</span>
                  </div>
                  
                  <p className="text-xs text-gray-400 leading-relaxed mb-6 h-12 overflow-hidden">{plan.description}</p>

                  <ul className="space-y-4 mb-8">
                    <li className="flex items-center gap-3 text-xs text-gray-300">
                      <Check size={14} className="text-emerald-400 shrink-0" />
                      <span>Reach <strong>{plan.reach_limit}</strong> customers in city</span>
                    </li>
                    <li className="flex items-center gap-3 text-xs text-gray-300">
                      {plan.whatsapp_enabled ? (
                        <Check size={14} className="text-emerald-400 shrink-0" />
                      ) : (
                        <Check size={14} className="text-gray-600 shrink-0 opacity-40" />
                      )}
                      <span className={plan.whatsapp_enabled ? 'text-gray-300' : 'text-gray-600 line-through opacity-50'}>
                        WhatsApp outreach support
                      </span>
                    </li>
                    <li className="flex items-center gap-3 text-xs text-gray-300">
                      {plan.facebook_enabled ? (
                        <Check size={14} className="text-emerald-400 shrink-0" />
                      ) : (
                        <Check size={14} className="text-gray-600 shrink-0 opacity-40" />
                      )}
                      <span className={plan.facebook_enabled ? 'text-gray-300' : 'text-gray-600 line-through opacity-50'}>
                        Facebook Page outreach
                      </span>
                    </li>
                    <li className="flex items-center gap-3 text-xs text-gray-300">
                      <Check size={14} className="text-emerald-400 shrink-0" />
                      <span>Auto-matching by city &amp; category</span>
                    </li>
                  </ul>
                </div>

                <a
                  href={getBillingActionUrl(planId)}
                  className={`w-full text-center py-3 rounded-xl text-xs font-semibold transition-all duration-200 block ${
                    isPro 
                      ? 'bg-indigo-600 text-white hover:bg-indigo-500 hover:shadow-[0_0_15px_rgba(99,102,241,0.3)]' 
                      : 'border border-white/10 text-gray-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {userAuthenticated ? 'Subscribe Now' : 'Register to Subscribe'}
                </a>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Feature Comparison Table */}
      <div className="max-w-5xl mx-auto mb-24 relative z-10">
        <h4 className="font-heading text-xl font-bold text-white text-center mb-10">Compare Features</h4>
        <div className="overflow-hidden border border-white/5 rounded-3xl glass">
          <table className="w-full text-left border-collapse text-xs sm:text-sm">
            <thead>
              <tr className="border-b border-white/5 bg-gray-950/40">
                <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Features</th>
                {plans.map(p => (
                  <th key={p.tier} className="p-4 text-xs font-bold text-white uppercase tracking-wider text-center">{p.name}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <tr>
                <td className="p-4 text-gray-300 font-medium">Outreach Reach Limit</td>
                {plans.map(p => (
                  <td key={p.tier} className="p-4 text-center text-white font-bold">{p.reach_limit}</td>
                ))}
              </tr>
              <tr>
                <td className="p-4 text-gray-300 font-medium">WhatsApp Delivery</td>
                {plans.map(p => (
                  <td key={p.tier} className="p-4 text-center">
                    {p.whatsapp_enabled ? <Check size={16} className="text-emerald-400 mx-auto" /> : <span className="text-gray-600">—</span>}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="p-4 text-gray-300 font-medium">Facebook Messenger Integration</td>
                {plans.map(p => (
                  <td key={p.tier} className="p-4 text-center">
                    {p.facebook_enabled ? <Check size={16} className="text-emerald-400 mx-auto" /> : <span className="text-gray-600">—</span>}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="p-4 text-gray-300 font-medium">Auto City Matchmaker</td>
                {plans.map(p => (
                  <td key={p.tier} className="p-4 text-center">
                    <Check size={16} className="text-emerald-400 mx-auto" />
                  </td>
                ))}
              </tr>
              <tr>
                <td className="p-4 text-gray-300 font-medium">Priority Processing</td>
                {plans.map(p => (
                  <td key={p.tier} className="p-4 text-center">
                    {p.tier !== 'basic' ? <Check size={16} className="text-emerald-400 mx-auto" /> : <span className="text-gray-600">—</span>}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* FAQ Accordion */}
      <div className="max-w-3xl mx-auto mb-24 relative z-10">
        <h4 className="font-heading text-xl font-bold text-white text-center mb-10">Frequently Asked Questions</h4>
        <div className="space-y-4">
          {FAQS.map((faq, idx) => {
            const isOpen = openFaqIndex === idx;
            return (
              <div key={idx} className="glass rounded-2xl border border-white/5 overflow-hidden">
                <button
                  onClick={() => setOpenFaqIndex(isOpen ? null : idx)}
                  className="w-full p-5 text-left text-sm font-semibold text-white flex justify-between items-center transition-colors hover:bg-white/[0.01]"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    size={16}
                    className={`text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180 text-white' : ''}`}
                  />
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="p-5 pt-0 text-xs sm:text-sm text-gray-400 leading-relaxed border-t border-white/5">
                        {faq.a}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </div>

      {/* Call to Action */}
      <div className="max-w-4xl mx-auto mb-16 relative z-10">
        <div className="glass p-8 sm:p-12 rounded-3xl border border-white/5 text-center relative overflow-hidden shadow-2xl bg-gradient-to-r from-indigo-500/5 to-purple-500/5">
          <div className="absolute -top-12 -right-12 w-48 h-48 bg-indigo-500/5 blur-[50px] rounded-full"></div>
          
          <h3 className="font-heading text-2xl sm:text-4xl font-extrabold text-white mb-4">Start Growing Your Business Today</h3>
          <p className="text-gray-400 text-sm sm:text-base max-w-lg mx-auto leading-relaxed mb-8">
            Create an account, set up your profile, and let our automated matchmaker find customers in your city.
          </p>
          <a
            href={registerUrl}
            className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 hover:shadow-[0_0_20px_rgba(99,102,241,0.4)] transition-all duration-300"
          >
            Create Your Account <ArrowRight size={14} />
          </a>
        </div>
      </div>

      {/* Trust Seal Footer */}
      <div className="max-w-xl mx-auto text-center text-xs text-gray-500 flex items-center justify-center gap-2">
        <ShieldCheck size={14} className="text-indigo-400" />
        Payments are processed securely via Razorpay. Cancel or change plans at any time.
      </div>
    </div>
  );
}
