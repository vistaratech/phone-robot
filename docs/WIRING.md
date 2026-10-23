# Wiring

```
3S LiPo 11.1 V --[fuse]--[switch]--+--> servo power bus (U2D2 Power Hub or your own distribution) --> 13x XL430
                                   +--> 5 V buck --> SBC (5 V pin / USB-C)
SBC --USB--> U2D2 --TTL (data)--> servo daisy-chain(s)
Phone <--Wi-Fi--> SBC            (phone has NO wire to the robot)
```

- XL430 supply range is roughly 6.5-12 V; 3S (9-12.6 V) is in range - confirm in the datasheet.
- Split the servos into 3 TTL chains (torso+left leg / right leg ...) so a single cable carries less current. All data lines
  share the one U2D2 TTL port; give every servo a unique ID (docs/SERVO_SETUP.md).
- Put the fuse close to the battery. Stall current of many servos at once can be large - start with a conservative fuse and
  a bench power supply with current limit for first tests.
- Common ground between buck converter, SBC, U2D2 and servo bus.
- Never charge/discharge a LiPo unattended; set a low-voltage cutoff (~3.3 V/cell under load).
