+++
title = "What Working with Agents Is Teaching Me #1: Feedback Loops"
date = 2026-04-03T23:52:40-07:00
draft = false
description = "Clear, actionable feedback loops help agents improve, and they reveal how much human growth depends on the same pattern."
tags = ["ai", "feedback loops", "reflection", "learning"]
categories = ["AI", "Thinking"]
toc = true
readingTime = true
featured = false
+++
Recently I've been spending more time working with coding agents. One thing that stood out quickly is how much their performance depends on the **feedback loop around them**. When the evaluation is clear and actionable, agents tend to improve over successive attempts in a surprisingly consistent way.

Watching that happen made me reflect on something simpler: how feedback
loops shape human behavior too.

---

## The Dentist Problem

There are many small things I do every day that I rarely rethink.

Take brushing teeth.

I've been doing it twice a day for decades. I don't think about the angle of the brush, the pressure, or whether I'm consistently reaching the gum line. It's muscle memory.

Then I go to the dentist.

Suddenly there's feedback:

-   I'm brushing too hard
-   I'm missing spots
-   I should hold the brush at a 45° angle

And it hits me: I've probably been repeating the same imperfect routine
for years.

Daily actions tend to drift into autopilot. Once something works "well enough," I stop evaluating it. Improvement only happens when something interrupts the loop, like a dentist appointment.

---

## The Strange Things I Never Revisited

Once I started noticing this, I realized how many small habits operate
the same way.

How many times do I rinse when washing dishes?  
What order do I wash things in?  
How do I wipe my kid after using the toilet, and how many tissues do I use?

These are things I've done thousands of times without thinking about
them.

But the moment I start **teaching a child**, I suddenly have to explain them.

And that's when I notice something strange: I've never really examined
the process myself.

I pause and ask:

-   Wait, what's the right way to do this?
-   Why do I do it this way?
-   Is there actually a better way?

Teaching forces awareness. It turns automatic behavior into something
observable.

---

## Injecting Awareness

The hardest step in a feedback loop isn't evaluation.

It's realizing evaluation is needed at all.

In *Think Again: The Power of Knowing What You Don't Know* by Adam Grant, the idea is that people often operate in modes that protect existing beliefs. I tend to defend what I already think rather than questioning it.

Improvement requires shifting into what he calls **scientist mode**: treating assumptions as hypotheses rather than facts.

That mindset injects awareness into everyday actions.

Instead of assuming the current approach is correct, I start asking:

-   Why do I do it this way?  
-   Is there a better approach?  
-   What signal tells me if it's working?

Often something external triggers that reflection. A dentist visit. A
code review. A production incident.

Or simply trying to teach someone else.

---

## Agents Make This Very Obvious

Working with agents made this dynamic even clearer.

When I teach an agent to do something, I have to explain the task precisely. I need to define the expected output, the constraints, and the signals that determine whether the result is correct.

In other words, I have to build the **evaluation loop**.

Agents tend to perform much better when the evaluation is **correct and actionable**.

For example:

Weak evaluation:

> The output is wrong.

Actionable evaluation:

> The API call ignored the pagination parameter. Retry using `page_token`.

The second type of feedback changes the next attempt.

With the right loop, the process becomes:

attempt → evaluation → correction → retry

Over multiple iterations, the system often converges toward a working
solution even if the first attempt was poor.

---

## Teaching Agents Changed How I Delegate

Teaching agents also made me notice something uncomfortable about how I delegate to people.

I often assume that if someone is capable and context is obvious to me, then the task is already well specified. But capability is not the same thing as shared context. A lot of delegation failure is not about effort or intelligence. It is about hidden assumptions.

When a result comes back slightly off, the easiest reaction is:

> This isn't what I meant.

But that response hides the most important part of the problem: **what exactly was misaligned?**

Was the goal unclear?  
Was the tradeoff wrong?  
Was the person optimizing for speed when I cared about completeness?  
Did I fail to say what "good" looked like?

Working with agents makes this painfully obvious because they expose every gap in the handoff. They do exactly what the prompt and evaluation loop support, not what I vaguely hoped they would infer.

That has made me think of delegation less as assigning work and more as transferring judgment. If I want a good outcome, I need to communicate not just the task, but the objective, the constraints, and the signals that should guide decisions when reality gets messy.

Good delegation is not:

> Do this.

It is closer to:

> Here is what success looks like. Here is what matters most. Here is where I want you to use judgment, and here is where I want you to check back with me.

That shift matters because the real bottleneck in delegation is often not execution. It is calibration.

The better I can make my evaluation criteria visible, the more likely the next attempt, by an agent or a person, gets closer to what I actually want.

---

## The Quiet Compounding Effect

The interesting thing about feedback loops is that they compound
quietly.

Small corrections applied repeatedly produce large improvements over
time.

The difference between brushing slightly wrong and slightly right isn't visible after one day. But over years, it becomes obvious.

Working with agents made me notice how many parts of my daily routines and work processes run without tight feedback loops.

The systems that improve fastest aren't necessarily the most powerful
ones.

They're the ones where the distance between **action and evaluation is
short**.

## Reference

- [*Think Again: The Power of Knowing What You Don't Know* by Adam Grant](https://www.amazon.com/Think-Again-Power-Knowing-What/dp/1984878107)
  What stayed with me from Grant's book is the contrast between defending what we already believe and treating our beliefs as things to test. That idea fits this essay closely: better feedback loops often begin when we stop assuming our current way is correct and start looking at it with more curiosity.
