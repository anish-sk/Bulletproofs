Instructions for running the code:

1) By following the given instructions here (https://www.alphr.com/ova-virtualbox/), import the ova file from the following google drive folder (https://drive.google.com/drive/folders/18gSoAiT9YIU9QUlo6UZ35oI9s2ZGKhUO?usp=sharing) into Oracle VirtualBox as a virtual machine.
2) The VM is a Ubuntu (64-bit) machine. The username is "cs6500" and the password is "cs6500".
3) Once inside the VM, open the terminal by pressing Ctrl+Alt+T. You will get to the home directory(~).
4) Change directory into the project directory by executing
   
   ``cd cs6500_project_bulletproofs``.
5) There are 3 main modules in our project:
	* Range Proofs - which is the core of our bulletproof technique and helps us to prove that a transaction amount lies in a given range without leaking information about the amount itself.
   * Fiat Shamir - this module implements the Fiat Shamir heuristic, which converts an interactive proof to a non-interactive proof.
   * Aggregating Range Proofs - this module implements a technique for aggregating multiple range proofs where the proof size only grows by an additive logarithmic factor based on the number of proofs to be aggregated, whereas in the standard method, the proof size grows by a multiplicative linear factor.
6) We know describe the procedure to run the codes for the above mentioned modules.


Range Proofs:

1) Change directory into the range proof directory
	
	 ``cd range_proof``.
2) Open another tab in the terminal.
3) The file i.txt contains values that are used to generate the required inputs for the prover and verifier. Namely it contains n (we prove that the transaction amount lies between 0 and 2^n - 1), p (the order of the group which is considered for the various operations, it is required that p is prime) and s (the seed for the random library). Note that n has to be a power of 2. The default value of n used is 32. If you choose to change this then it has to be updated in the prover and verifier files.
4) Run the following command in either of the terminal tabs:
   
	``python3 generate_inputs_range_proof.py < i.txt``.
5) The program will run and generate inputs and store them in the files "v", "gamma" and "V".
6) In the first terminal tab, run the following command for running the prover. Let the seed you entered in i.txt be "1000" and the port that you want the prover to listen at be "1234". Then:

	 ``python3 range_proof_prover.py -p 1234 -v $(cat v) -g $(cat gamma) -s 1000``.
7) In the second terminal tab, run the following command for running the verifier. Let the seed you entered in i.txt be "1000" and the port that the prover is listening at be "1234". Then:

	``python3 range_proof_verifier.py -a 127.0.0.1 -p 1234 -V $(cat V) -s 1000``.

   In case you wish to run the prover on a separate machine, then you will need to change the -a argument appropriately.
8) The prover and verifier will run, interact and complete the proof. If the prover implementation is correct you will get the following message at the end of the verifier's execution: "Verification successfull!!" 

Fiat Shamir:

1) Change directory into the fiat shamir directory
	
	 ``cd fiat-shamir``.
2) The file i.txt contains values that are used to generate the required inputs for the prover and verifier. Namely it contains n (we prove that the transaction amount lies between 0 and 2^n - 1), p (the order of the group which is considered for the various operations, it is required that p is prime) and s (the seed for the random library). Note that n has to be a power of 2. The default value of n used is 32. If you choose to change this then it has to be updated in the prover and verifier files.
3) Run the following command in the terminal:
   
	``python3 generate_inputs_range_proof.py < i.txt``.
4) The program will run and generate inputs and store them in the files "v", "gamma" and "V".
5) In the terminal, run the following command for running the prover. Let the seed you entered in i.txt be "1000". Then:

	 ``python3 range_proof_prover.py -v $(cat v) -g $(cat gamma) -s 1000``.
6) The prover will run and store certain logs in the file "transcript" which will be later used by the verifier.
7) In the terminal, run the following command for running the verifier. Let the seed you entered in i.txt be "1000". Then:

	``python3 range_proof_verifier.py -V $(cat V) -s 1000``.

8) The verifier will run and complete the proof. If the prover implementation is correct you will get the following message at the end of the verifier's execution: "Verification successfull!!" 


Aggregating Range Proofs:

1) Change directory into the aggregating range proof directory
	
	 ``cd aggregate_range_proof``.
2) Open another tab in the terminal.
3) The file i.txt contains values that are used to generate the required inputs for the prover and verifier. Namely it contains n (we prove that the transaction amount lies between 0 and 2^n - 1), m (number of proofs to be aggregated), p (the order of the group which is considered for the various operations, it is required that p is prime) and s (the seed for the random library). Note that n*m should be a power of 2. The default values of n and m used are 32 and 4 respectively. If you choose to change these then they have to be updated in the prover and verifier files.
4) Run the following command in either of the terminal tabs:
   
	``python3 generate_inputs_aggregate_range_proof.py < i.txt``.
5) The program will run and generate inputs and store them in the files "v", "gamma" and "V".
6) In the first terminal tab, run the following command for running the prover. Let the seed you entered in i.txt be "1000" and the port that you want the prover to listen at be "1234". Then:

	 ``python3 aggregate_range_proof_prover.py -p 1234 -v $(cat v) -g $(cat gamma) -s 1000``.
7) In the second terminal tab, run the following command for running the verifier. Let the seed you entered in i.txt be "1000" and the port that the prover is listening at be "1234". Then:

	``python3 aggregate_range_proof_verifier.py -a 127.0.0.1 -p 1234 -V $(cat V) -s 1000``.

   In case you wish to run the prover on a separate machine, then you will need to change the -a argument appropriately.
8) The prover and verifier will run, interact and complete the proof. If the prover implementation is correct you will get the following message at the end of the verifier's execution: "Verification successfull!!" 