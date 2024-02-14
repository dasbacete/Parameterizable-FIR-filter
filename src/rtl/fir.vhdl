library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.MATH_REAL.ALL;

entity FIR is
	generic(
		WGTW: integer := 8;
		DW:   integer := 16;
		N_SG: integer := 4;
		constant WAW: integer;
		constant OW:  integer);
	Port(
		clk:      in  std_logic;
		rst:      in  std_logic;
		stb_in:   in  std_logic;
		calc:     in  std_logic;
		bsy_in:   in  std_logic;
		data_in:  in  signed (DW-1 downto 0);
		wgt_addr: in 	unsigned (WAW-1 downto 0);
		wgt_in:   in  signed (WGTW-1 downto 0);
		stb_out:  out std_logic;
		bsy_out:  out std_logic;
		data_out: out signed (OW-1 downto 0));
end FIR;

architecture Behavioral of FIR is

	component SG is
		generic (
			DW:  integer := 16;
			SW_IN:  integer := 16;
			SW_OUT: integer := 16;
			WGTW:   integer := 8);
		Port(
			clk:     in  std_logic;
			rst:     in  std_logic;
			stb_in:  in  std_logic;
			bsy_in:  in  std_logic;
			sum_in:  in  signed (SW_IN-1 downto 0);
			wgt:     in  signed (WGTW-1 downto 0);
			dly_in:  in  signed (DW-1 downto 0);
			stb_out: out std_logic;
			dly_out: out signed (DW-1 downto 0);
			sum_out: out signed (SW_OUT-1 downto 0));
	end component;

	type t_array_w is array (0 to N_SG-1) of signed(WGTW-1 downto 0);
  type t_array_d is array (0 to N_SG-1) of signed(DW-1 downto 0);
  type t_array_s is array (0 to N_SG-1) of signed(OW-1 downto 0);

	signal weights:   t_array_w ;
	signal dly_data:  t_array_d ;
	signal sum_data:  t_array_s ;
	signal fst_sum:   std_logic_vector (DW-1 downto 0);
	signal stb:       std_logic_vector (N_SG-1 downto 0);
begin

	-- ctrl
	bsy_out <= bsy_in;
	stb_out <= or stb(N_SG-1 downto 0);
	stb(0) <= calc and stb_in;

	process (clk)
	begin
		if rising_edge(clk) then
			if (calc = '0') then
				weights(to_integer(wgt_addr)) <= wgt_in;
			end if;
		end if;
	end process;

	--1st stage
	dly_data(0) <= data_in;
	sum_data(0) <=  resize(data_in * weights(0), sum_data(0)'length);

	-- intermediate stages
	SGs: for i in 0 to N_SG-2 generate
		-- declare here the datawidths & inout signals
		constant SG_DW_IN:  integer := DW + WGTW + integer(ceil(log2(real(i+1))));
		constant SG_DW_OUT: integer := DW + WGTW + integer(ceil(log2(real(i+2))));
		signal   output:    signed (SG_DW_OUT-1 downto 0);
	begin
		stage_n: SG
			generic map ( DW      => DW,
			              SW_IN   => SG_DW_IN,
				          SW_OUT  => SG_DW_OUT,
			              WGTW    => WGTW )
			   port map ( clk     => clk,
                    rst     => rst,
					          stb_in  => stb(i),
							 	    bsy_in  => bsy_in,
							 	    sum_in  => sum_data(i)(SG_DW_IN-1 downto 0),
							 	    wgt     => weights(i+1),
							 	    dly_in  => dly_data(i),
							      stb_out => stb(i+1),
							      dly_out => dly_data(i+1),
							 	    sum_out => output);
		sum_data(i+1) <= resize(output,sum_data(i+1)'length);
	end generate SGs;

--lst stage
	data_out <= dly_data(N_SG-1) * weights(N_SG-1) + sum_data(N_SG-1);

end Behavioral;
