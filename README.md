# Proiect-TCM
Protocolul de autentificare zero-knowledge Feige-Fiat-Shamir (in Zn)

# 1. Generare chei
```python main.py keygen --name alice --bits 256 --k 5```

# 2. Autentificare locală
```python main.py auth --name alice --t 4```

# 3. Autentificare locală (verbose)
```python main.py auth --name alice --t 4 --verbose```

# 4. Autentificare prover–verifier
```python verifier.py --name alice --t 4```

# 5. Autentificare prover–verifier (verbose)
```python verifier.py --name alice --t 4 --verbose```

# 6. Demonstrare atac
```python attack_demo.py --name alice --k 5 --t 4 --trials 2000```